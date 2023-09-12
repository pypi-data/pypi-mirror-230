from __future__ import annotations

from datetime import datetime
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from urllib import parse, request
import urllib.error
import uuid

import numpy as np
import pandas as pd


os.environ['IGNORE_QHOME'] = '1'
os.environ['PYKX_NOQCE'] = '1'
os.environ['SKIP_UNDERQ'] = '1'
os.environ['QARGS'] = '--unlicensed'
import pykx as kx  # noqa: E402


MAX_QIPC_SERIALIZATION_SIZE = 10*1024*1024  # 10MB

# Minimum datetime/timestmp supported by q/kdb+
MIN_DATETIME = datetime(1707, 9, 22, 0, 12, 43, 145224)
# Maximum datetime/timestamp supported by q/kdb+
MAX_DATETIME = datetime(2262, 4, 11, 23, 47, 16, 854775)


_qtype_to_dtype = dict(
    boolean='bool',
    guid='str',
    byte='uint8',
    short='int16',
    int='int32',
    long='int64',
    real='float32',
    float='float64',
    string='bytes',
    symbol='str',
    timestamp='datetime64[ns]',
    month='datetime64[M]',
    date='datetime64[D]',
    timespan='timedelta64[ns]',
    minute='timedelta64[m]',
    second='timedelta64[s]',
    time='timedelta64[ms]',
)
_dtype_to_qtype = {v: k for k, v in _qtype_to_dtype.items()}
for key in list(_qtype_to_dtype.keys()):
    _qtype_to_dtype[f'{key}s'] = _qtype_to_dtype[key]


class Session:
    """Session represents a connection to a KDB.AI instance."""

    PROTOCOL  = 'https'
    HOST   = 'localhost'
    PORT   = 443

    READY_PATH  = '/api/v1/ready'
    CONFIG_PATH = '/api/v1/config/table'
    CREATE_PATH = '/api/v1/config/table/%s'
    DROP_PATH   = '/api/v1/config/table/%s'
    QUERY_PATH  = '/api/v1/data'
    INSERT_PATH = '/api/v1/insert'
    TRAIN_PATH  = '/api/v1/train'
    SEARCH_PATH = '/api/v1/kxi/search'

    def __init__(
        self,
        api_key = None,
        *,
        endpoint = 'http://localhost:8082'
    ):
        """Create a REST API connection to a KDB.AI endpoint.

        Args:
            api_key (str): API Key to be used for authentication.
            endpoint (str): Server endpoint to connect to.

        Example:
            Open a session on KDB.AI Cloud with an api key:

            ```python
            session = Session(api_key='YOUR_API_KEY')
            ```

            Open a session on a custom KDB.AI instance on http://localhost:8082:

            ```python
            session = kdbai.Session(endpoint='http://localhost:8082')
            ```
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self._check_endpoint()
        self._check_readiness()

    def _check_endpoint(self):
        try:
            url = parse.urlparse(self.endpoint)
            assert url.scheme in ('http', 'https')
            assert url.netloc != ''
        except Exception:
            raise KDBAIException(f'Invalid URL: {self.endpoint}.')
        return True

    def _check_readiness(self):
        try:
            assert self._test_readiness()
        except Exception:
            raise KDBAIException(
                f'Failed to open a session on {self.endpoint} with API key {self.api_key}. '
                'Please double check your `endpoint` and `api_key`.'
                )

    def _test_readiness(self):
        return self._rest_get(Session.READY_PATH) == 'OK'

    def _wait_for_readiness(self, timeout=10):
        i = 0
        while True:
            try:
                if self._test_readiness():
                    break
            except Exception:
                pass
            time.sleep(1)
            i += 1
            if i > timeout:
                return False
        return True

    def list(self) -> List[str]:
        """Retrieve the list of tables.

        Returns:
            A list of strings with the names of the existing tables.

        Example:
            ```python
            session.list()
            ["trade", "quote"]
            ```
        """
        try:
            return self._list()
        except Exception:
            raise KDBAIException('Failed to retrieve the list of tables.')

    def table(self, name: str) -> Table:
        """Retrieve an existing table which was created in the previous session.

        Args:
            name (str): Name of the table to retrieve.

        Returns:
                A `Table` object representing the KDB.AI table.

        Example:
            Retrieve the `trade` table:

            ```python
            session1 = kdbai.Session(host='localhost',port=8082, protocol='http') # Previous session
            table1 = session1.create_table('trade1', schema)                      # Create table 'trade1'

            session2 = kdbai.Session(host='localhost',port=8082, protocol='http') # Current session
            table2 = session2.table("trade1")                                     # Retrieve table 'trade1'
            ```
        """
        return Table(name=name, session=self)

    def create_table(self, name, schema) -> Table:
        """Create a table with a schema

        Args:
            name (str): Name of the table to create.
            schema (dict): Schema of the table to create. This schema must contain a list of columns. All columns
                must have either a `pytype` or a `qtype` specified except the column of vectors.
                One column of vector embeddings may also have a `vectorIndex` attribute with the configuration of the
                index for similarity search - this column is implicitly an array of `float32`.

        Returns:
                A newly created `Table` object based on the schema.

        Raises:
            KDBAIException: Raised when a error happens during the creation of the table.

        Example Flat Index:
            ```python
            schema = {'columns': [{'name': 'id', 'pytype': 'str'},
                                  {'name': 'tag', 'pytype': 'str'},
                                  {'name': 'text', 'pytype': 'bytes'},
                                  {'name': 'embeddings',
                                   'vectorIndex': {'dims': 1536, 'metric': 'L2', 'type': 'flat'}}]}
            table = session.create_table('documents', schema)
            ```

        Example IVF Index:
            ```python
            schema = {'columns': [{'name': 'id', 'pytype': 'str'},
                                  {'name': 'tag', 'pytype': 'str'},
                                  {'name': 'text', 'pytype': 'bytes'},
                                  {'name': 'embeddings',
                                   'vectorIndex': {'trainingVectors': 1000,
                                                   'metric': 'CS',
                                                   'type': 'ivf',
                                                   'nclusters': 10}}]}
            table = session.create_table('documents', schema)
            ```

        Example IVFPQ Index:
            ```python
            schema = {'columns': [{'name': 'id', 'pytype': 'str'},
                                  {'name': 'tag', 'pytype': 'str'},
                                  {'name': 'text', 'pytype': 'bytes'},
                                  {'name': 'embeddings',
                                   'vectorIndex': {'trainingVectors': 5000,
                                                   'metric': 'L2',
                                                   'type': 'ivfpq',
                                                   'nclusters': 50,
                                                   'nsplits': 8,
                                                   'nbits': 8}}]}
            table = session.create_table('documents', schema)
            ```

        Example HNSW Index:
            ```python
            schema = {'columns': [{'name': 'id', 'pytype': 'str'},
                                  {'name': 'tag', 'pytype': 'str'},
                                  {'name': 'text', 'pytype': 'bytes'},
                                  {'name': 'embeddings',
                                   'vectorIndex': {'dims': 1536,
                                                   'metric': 'IP',
                                                   'type': 'hnsw',
                                                   'efConstruction' : 8, 'M': 8}}]}
            table = session.create_table('documents', schema)
            ```
        """
        try:
            schema = self._format_schema_to_q(schema)
            self._create_table(name, schema)

            time.sleep(10)

            if self._wait_for_readiness(timeout=10):
                return Table(name=name, session=self)
            else:
                raise KDBAIException(f'Failed to create the new table named {name} with schema {schema}'
                                     ' because of timeout expiration.')
        except urllib.error.HTTPError as e:
            raise KDBAIException(f'Failed to create the new table named {name} with schema {schema}.', e=e)
        except KDBAIException as e:
            raise e
        except Exception:
            raise KDBAIException(f'Failed to create the new table named {name} with schema {schema}.')

    def _format_schema_to_q(self, schema):
        out = {}
        out['type'] = 'splayed'
        out['columns'] = []
        for column in schema['columns']:
            out_col = dict(name=column['name'])

            if 'qtype' in column:
                out_col['type'] = column['qtype']
            elif 'pytype' in column:
                out_col['type'] = _dtype_to_qtype[column['pytype']]

            if 'vectorIndex' in column:
                out_col['vectorIndex'] = column['vectorIndex']
                out_col['type'] = 'reals'

            if 'type' not in out_col:
                raise KDBAIException('Invalid column, missing `pytype` or `qtype`.')

            out['columns'].append(out_col)
        return out

    def _create_table(self, name, schema):
        body = self._rest_post_json(self.CREATE_PATH % name, schema)
        return self._create_table_status(body)

    def _create_table_status(self, body):
        if 'message' in body and body['message'] == 'success':
            return True
        else:
            raise KDBAIException(body)

    def _config(self):
        return self._rest_get_json(Session.CONFIG_PATH)

    def _list(self):
        config = self._config()
        tables = list(config.keys())
        return tables

    def _rest_get(self, path):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        req = self._rest_request('GET', path, headers)
        res = request.urlopen(req)
        return res.read().decode('utf-8')

    def _rest_get_json(self, path):
        body = json.loads(self._rest_get(path))
        return body

    def _rest_post_json(self, path, data):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        data = json.dumps(data).encode('utf-8')
        req = self._rest_request('POST', path, headers, data)
        res = request.urlopen(req)
        body = json.loads(res.read().decode('utf-8'))
        return body

    def _rest_post_json_to_qipc(self, path, data):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/octet-stream'}
        data = json.dumps(data).encode('utf-8')
        req = self._rest_request('POST', path, headers, data)
        res = request.urlopen(req)
        res = kx._wrappers.deserialize(res.read())._unlicensed_getitem(1)
        return self._format_qipc_result(res)

    def _rest_post_qipc(self, path, table, data, guid = False):
        headers = {'Content-type': 'application/octet-stream',
                   'Accept': 'application/json'}
        if guid:
            data = bytes(kx._wrappers.k_pickle(kx.toq([uuid.uuid4(), table, data])))
        else:
            data = bytes(kx._wrappers.k_pickle(kx.toq([table, data])))
        if len(data) > MAX_QIPC_SERIALIZATION_SIZE:
            raise KDBAIException(
                f'The maximum serialized size of the data to insert is {MAX_QIPC_SERIALIZATION_SIZE} bytes. '
                f'The size of your serialized data is {len(data)} bytes. '
                'Please insert your data by smaller batches.'
                )
        req = self._rest_request('POST', path, headers, data)
        res = request.urlopen(req)
        return self._format_json_result(res.read().decode('utf-8'))

    def _rest_delete(self, path):
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        req = self._rest_request('DELETE', path, headers)
        res = request.urlopen(req)
        body = json.loads(res.read().decode('utf-8'))
        return body

    def _rest_request(self, method, path, headers, data = None):
        url = self._build_url(path)
        if self.api_key is not None:
            headers['X-Api-Key'] = self.api_key
        return request.Request(url, method=method, headers=headers, data=data)

    def _build_url(self, path):
        return self.endpoint + path

    def _format_qipc_result(self, res):
        if isinstance(res, kx.Table):
            return res.pd()
        elif isinstance(res, kx.List):
            result = []
            for i in range(len(res)):
                result.append(res._unlicensed_getitem(i).pd())
            return result
        else:
            raise KDBAIException('Not implemented.')

    def _format_json_result(self, res):
        try:
            r = json.loads(res)
            if 'message' in r:
                return r['message']
        except json.decoder.JSONDecodeError:
            return True
        return True


class Table:
    """KDB.AI table."""

    def __init__(self, name: str, *, session: Session, **kwargs):
        """kdbai_client.Table

        Table object shall be created with `session.create_table(...)` or retrieved with `session.table(...)`.
        This constructor shall not be used directly.
        """
        self.name = name
        self.session = session

        try:
            tables = self.session._list()
        except urllib.error.HTTPError as e:
            raise KDBAIException('Failed to retrieve the list of tables.', e=e)
        except Exception:
            raise KDBAIException('Failed to retrieve the list of tables.')

        self._check_table_name(tables)

    def _check_table_name(self, tables: list):
        if self.name not in tables:
            raise KDBAIException(f'Failed to retrieve the table named: {self.name}.')
        return True

    def schema(self) -> Dict:
        """Retrieve the schema of the table.

        Raises:
            KDBAIException: Raised when an error occurs during schema retrieval

        Returns:
            A `dict` containing the table name
                and the list of column names and appropriate numpy datatypes.

        Example:
            ```python
            table.schema()

            {'columns': [{'name': 'id', 'pytype': 'str', 'qtype': 'symbol'},
                          {'name': 'tag', 'pytype': 'str', 'qtype': 'symbol'},
                          {'name': 'text', 'pytype': 'bytes', 'qtype': 'string'},
                          {'name': 'embeddings',
                           'pytype': 'float32',
                           'qtype': 'reals',
                           'vectorIndex': {'dims': 1536, 'metric': 'L2', 'type': 'flat'}}]}
            ```
        """
        try:
            config = self.session._config()
            schema = config[self.name]
            return self._format_schema_to_py(schema)
        except Exception:
            raise KDBAIException(f'Failed to retrieve the schema of table named: {self.name}.')


    def _format_schema_to_py(self, schema: dict):
        schema.pop('type')
        for column in schema['columns']:
            column['qtype'] = column.pop('type')
            column['pytype'] = self._translate_qtype(column['qtype'])
            if 'attrMem' in column:
                column.pop('attrMem')
        return schema

    def _translate_qtype(self, qtype: int):
        return _qtype_to_dtype.get(qtype, 'object')

    def _validate_dataframe(self, data: pd.DataFrame, warn:Optional[bool] = True):
        if not isinstance(data, pd.DataFrame):
            raise KDBAIException('`data` should be a pandas.DataFrame.')
        else:
            if (data.index.values != np.arange(len(data))).any():
                if warn:
                    logging.warning('`data` DataFrame has a non trivial index. It will be dropped before insertion.')
                data = data.reset_index(drop=True)
        return data

    def train(self, data: pd.DataFrame, warn:Optional[bool] = True) -> str:
        """Train the index (IVF and IVFPQ only).

        Args:
            data (DataFrame): Pandas dataframe with column names/types matching the target table.
            warn (bool): If True, display a warning when `data` has a trivial which will be dropped before training.

        Returns:
            A `string` containing the status after training

        Examples:
            ```python
            ROWS = 50
            DIMS = 10

            data = {
                "time": [timedelta(microseconds=np.random.randint(0, int(1e10))) for _ in range(ROWS)],
                "sym": [f"sym_{np.random.randint(0, 999)}" for _ in range(ROWS)],
                "realTime": [datetime.utcnow() for _ in range(ROWS)],
                "price": [np.random.rand(DIMS).astype(np.float32) for _ in range(ROWS)],
                "size": [np.random.randint(1, 100) for _ in range(ROWS)],
            }
            df = pd.DataFrame(data)
            table.train(df)
            ```

        Raises:
            KDBAIException: Raised when an error occurs during training.
        """
        data = self._validate_dataframe(data, warn)

        try:
            return self.session._rest_post_qipc(Session.TRAIN_PATH, self.name, data)
        except urllib.error.HTTPError as e:
            raise KDBAIException(f'Failed to insert training data in table named: {self.name}.', e=e)
        except Exception:
            raise KDBAIException(f'Failed to insert training data in table named: {self.name}.')

    def insert(self, data: pd.DataFrame, warn: Optional[bool] = True) -> bool:
        """Insert data into the table.

        Args:
            data (DataFrame): Pandas dataframe with column names/types matching the target table.
            warn (bool): If True, display a warning when `data` has a trivial which will be dropped before insertion.

        Returns:
            A boolean which is True if the insertion was successful.

        Examples:
            ```python
            ROWS = 50
            DIMS = 10

            data = {
                "time": [timedelta(microseconds=np.random.randint(0, int(1e10))) for _ in range(ROWS)],
                "sym": [f"sym_{np.random.randint(0, 999)}" for _ in range(ROWS)],
                "realTime": [datetime.utcnow() for _ in range(ROWS)],
                "price": [np.random.rand(DIMS).astype(np.float32) for _ in range(ROWS)],
                "size": [np.random.randint(1, 100) for _ in range(ROWS)],
            }
            df = pd.DataFrame(data)
            table.insert(df)
            ```

        Raises:
            KDBAIException: Raised when an error occurs during insert.
        """
        data = self._validate_dataframe(data, warn)

        try:
            return self.session._rest_post_qipc(Session.INSERT_PATH, self.name, data, True)
        except urllib.error.HTTPError as e:
            raise KDBAIException(f'Failed to insert data in table named: {self.name}.', e=e)
        except Exception:
            raise KDBAIException(f'Failed to insert data in table named: {self.name}.')

    def query(
        self,
        filter: Optional[List[list]] = None,
        group_by: Optional[str] = None,
        aggs: Optional[List[list]] = None,
        sort_by: Optional[List[str]] = None,
        fill: Optional[str] = None,
    ) -> pd.DataFrame:
        """Query data from the table.

        Args:
            filter: A list of filter conditions as triplets in the following format:
                `[['function', 'column name', 'parameter'], ... ]`
                See all filter operators [here](https://code.kx.com/kdbai/use/filter.html#supported-filter-functions)
            group_by: A list of column names to use for group by.
            aggs: Either a list of column names to select or a list of aggregations to perform as a
                list of triplers in the following form:
                `[['output_column', 'agg_function', 'input_column'], ... ]`
                See all aggregation functions [here](https://code.kx.com/kdbai/use/query.html#supported-aggregations)
            sort_by: List of column names to sort on.
            fill: This defines how to handle null values. This should be either `'forward'` or `'zero'` or `None`.

        Returns:
            Pandas dataframe with the query results.

        Examples:
            ```python
            table.query(group_by = ['sensorID', 'qual'])
            table.query(filter = [['within', 'qual', [0, 2]]])
            ```

        Raises:
            KDBAIException: Raised when an error occurs during query.
        """
        params: Dict[str, Any] = {"table": self.name}

        optional_params_map = (
            ("filter", filter),
            ("groupBy", group_by),
            ("agg", aggs),
            ("fill", fill),
            ("sortCols", sort_by),
        )
        for key, value in optional_params_map:
            if value is not None:
                params[key] = value

        try:
            return self.session._rest_post_json_to_qipc(Session.QUERY_PATH, params)
        except urllib.error.HTTPError as e:
            raise KDBAIException(
                f'Failed to process the query {params} on table named: {self.name}.', e=e)
        except Exception:
            raise KDBAIException(
                f'Failed to process the query {params} on table named: {self.name}.')

    def search(
        self,
        vectors: List[List],
        n: int = 1,
        index_options: Optional[dict] = None,
        distances: Optional[str] = None,
        filter: Optional[List[list]] = None,
        group_by: Optional[str] = None,
        aggs: Optional[List[list]] = None,
        sort_by: Optional[List[str]] = None,
    ) -> List[pd.DataFrame]:
        """Perform similarity search on the table.

        Args:
            vectors (list of lists): Query vectors for the search.
            n (int): Number of neighbours to return.
            index_options (dict): Index specific options for similarity search.
            distances (str): Optional name of a column to output the distances.
                If not specified, __nn_distance
                will be added as an extra column to the result table.
            filter: A list of filter conditions as triplets in the following format:
                `[['function', 'column name', 'parameter'], ... ]`
                See all filter operators [here](https://code.kx.com/kdbai/use/filter.html#supported-filter-functions)
            group_by: A list of column names to use for group by.
            aggs: Either a list of column names to select or a list of aggregations to perform as a
                list of triplers in the following form:
                `[['output_column', 'agg_function', 'input_column'], ... ]`
                See all aggregation functions [here](https://code.kx.com/kdbai/use/query.html#supported-aggregations)
            sort_by: List of column names to sort on.

        Returns:
            List of Pandas dataframes with one dataframe of matching neighbors for each query vector.

        Examples:
            ```python
            #Find the closest neighbour of a single query vector
            table.search(vectors=[[0,0,0,0,0,0,0,0,0,0]], n=1)

            #Find the 3 closest neighbours of 2 query vectors
            table.search(vectors=[[0,0,0,0,0,0,0,0,0,0], [1,1,1,1,1,1,1,1,1,1]], n=3)

            # With aggregation and sorting
            table.search(vectors=[[0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1,1,1]],
            n=3,
            aggs=[['sumSize','sum','size']],
            group_by=['sym'],
            sort_by=['sumSize'])

            # Filter
            table.search(vectors=[[0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1,1,1]],
            n=3,
            filter=[['within','size',(5,999)],['like','sym','AAP*']])

            # Customized distance name
            table.search(vectors=[[0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1,1,1]],
            n=3,
            distances='myDist')
            ```

        Raises:
            KDBAIException: Raised when an error occurs during search.
        """
        params: Dict[str, Any] = {"table": self.name}

        params['vectors'] = vectors
        params['n'] = n

        optional_params_map = (
            ("distances", distances),
            ("filter", filter),
            ("groupBy", group_by),
            ("agg", aggs),
            ("sortCols", sort_by),
        )
        for key, value in optional_params_map:
            if value is not None:
                params[key] = value # type: ignore

        if index_options is not None:
            for key, value in index_options.items():
                params[key] = value

        try:
            return self.session._rest_post_json_to_qipc(Session.SEARCH_PATH, params)
        except urllib.error.HTTPError as e:
            raise KDBAIException(
                f'Failed to process the query {params} on table named: {self.name}.', e=e)
        except Exception:
            raise KDBAIException(
                f'Failed to process the query {params} on table named: {self.name}.')

    def drop(self) -> bool:
        """Drop the table.

        Returns:
            A boolean which is True if the table was successfully dropped.

        Examples:
            ```python
            table.drop()
            ```

        Raises:
            KDBAIException: Raised when an error occurs during the table deletion.
        """
        try:
            body = self.session._rest_delete(Session.DROP_PATH % self.name)
            return self._drop_status(body)
        except urllib.error.HTTPError as e:
            raise KDBAIException(
                f'Failed to drop the table named: {self.name}.', e=e)
        except KDBAIException as e:
            raise e
        except Exception:
            raise KDBAIException(
                f'Failed to drop the table named: {self.name}.')

    def _drop_status(self, body):
        if 'message' in body and body['message'] == 'success':
            return True
        else:
            raise KDBAIException(body)

class KDBAIException(Exception):
    """KDB.AI exception."""

    def __init__(self, msg, e = None, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
        self.e = e
        if self.e is not None:
            reason = None
            data = self.e.fp.read()
            try:
                if (self.e.getcode() == 400
                    and self.e.headers.get('Content-type') == 'application/octet-stream'):
                    reason = kx._wrappers.deserialize(data).py()[0]['ai'].decode('utf-8')
                else:
                    reason = json.loads(data.decode('utf-8'))
            except Exception:
                reason = data.decode('utf-8')
            self.code = self.e.code
            if reason is not None:
                self.text = f'{msg[:-1]}, because of: {reason}.'
            self.args = (self.text,)
