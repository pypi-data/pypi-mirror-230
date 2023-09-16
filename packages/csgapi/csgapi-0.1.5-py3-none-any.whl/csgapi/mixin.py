from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Type, Generator

import csgapi.base as base
from csgapi.base import Inequality, Order, CSGError
from csgapi.client import CSGList, CSGenome
import csgapi.utils as exc


__all__ = [
    "GetMixin",
    "ListMixin",
    "CreateMixin",
    "UpdateMixin",
    "DeleteMixin",
    "SaveMixin",
    "ObjectDeleteMixin",
]


_RestManagerBase = base.RESTManager
_RestObjectBase = base.RESTObject

class SaveMixin(_RestObjectBase):
    """Mixin for RESTObject's that can be updated."""

    _id_attr: Optional[str]
    _attrs: Dict[str, Any]
    _module: ModuleType
    _parent_attrs: Dict[str, Any]
    _updated_attrs: Dict[str, Any]
    manager: base.RESTManager

    def _get_updated_data(self):
        updated_data = {}
        for attr in self.manager._update_attrs.required:
            # Get everything required, no matter if it's been updated
            updated_data[attr] = getattr(self, attr)
        # Add the updated attributes
        updated_data.update(self._updated_attrs)

        return updated_data

    def save(self) -> Dict[str, Any]:
        """Save the changes made to the object to the server.

        The object is updated to match what the server returns.

        Args:
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The server response Dict

        Raise:
            CSGError if there was some server error
        """
        updated_data = self._get_updated_data()
        # Nothing to update. Server fails if sent an empty dict.
        if not updated_data:
            return None

        # call the manager
        obj_id = self.encoded_id
        server_data = self.manager.update(uid=obj_id, new_data=updated_data)
        self._update_attrs(server_data)
        return server_data


class ObjectDeleteMixin(_RestObjectBase):
    """Mixin for RESTObject's that can be deleted."""

    _id_attr: Optional[str]
    _attrs: Dict[str, Any]
    _module: ModuleType
    _parent_attrs: Dict[str, Any]
    _updated_attrs: Dict[str, Any]
    manager: base.RESTManager

    def delete(self, **kwargs: Any) -> None:
        """Delete the object from the server.

        Args:
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            CSGError if there was some server error
        """
        self.manager.delete(self.encoded_id, **kwargs)


class APIObject(SaveMixin, ObjectDeleteMixin):
    """
    This is simply a class for typing
    Represents an object built from server data.

    It holds the attributes know from the server, and the updated attributes in another. This allows smart updates, if the object allows it.
    """
    pass

class GetMixin(_RestManagerBase):
    def get(self, uid=None, params=None) -> APIObject:
        """Retrieve a single object.
        Args:
            uid: uid of the object to retrieve
            params: additional query parameters (e.g. filter, column)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The generated RESTObject.

        Raises:
            CSGError if there was some server error
        """
        if uid is None:
            raise CSGError({"errors": "uid not specified", "status": 400})
        if not isinstance(uid, int):
            raise CSGError({"errors": "uid has to be an integer", "status": 400})
        ## easy name stuff here ##
        incoming_filter = params or {}
        # for k,v in kwargs:
        #     if k in self._create_attrs.required:
        #         incoming_filter[k] = v
        server_data = self.csgenome.http_get(path=f'{self._path}/{uid}', params=incoming_filter)
        # print(f'server data: {server_data}')

        try:
            if 'data' in server_data.keys():
                res = server_data['data']  # TODO: very rigid implementation
                return self._obj_cls(self, res)
            else:
                raise CSGError(server_data)
        except KeyError:
            # there was somehow no errors key in the server response, so make a generic one and rethrow error
            server_data['errors'] = 'Error with request'
            raise CSGError(server_data)


class ListMixin(_RestManagerBase):
    _obj_cls: Optional[Type[base.RESTObject]]
    _path: Optional[str]
    csgenome: CSGenome

    def list(self, dictionary: Dict[str, Any] = None, columns: str | List[str] = None, exact=False,
             order_by: str | Order | List[str | Order] = None,
             limit: int = None, **kwargs) -> List[APIObject]:
        """
        Returns a list of all objects of the table.
        You can pass in a dictionary containing key value pairs to search and filter records by,
        or use keyword parameters as key value pairs instead. In order to search for multiple values
        for a field, you can supply a list of values. Example below. In order to search for a numeric 
        or date column by an inequality, use the gt(), ge(), lt(), le(), or Range() functions from
        csgapi.base. Example also below.
        Kwargs:
            exact: True/False (default False)
                If exact, then string fields are case sensitive
            columns: List[str] | str
                Columns of the table to include in the search. If including a single column in
                search, you can use a string or a list of string columns to include multiple
            order_by: str | csgapi.base.Order | List[str | csgapi.base.Order]
                Orders the search by the str column provided, or if a list, then by all the columns
                in the order they are in the list. In order to order a column by descending order, 
                provice a csgapi.base.desc(column_name). Default ordering is ascending order,
                but you can provide a csgapi.base.asc(column_name) to make it clear to reviewers.
                csgapi.base.desc and csgapi.base.asc are csgapi.base.Order classes.
            limit: int
                If specified, the returned list is of length `limit`. i.e. The first `limit` records
                are returned. If there are less records that match the search than limit, then
                all records that match the search are returned.
        **kwargs: values for columns of the table you want to search for (if a dictionary if
        passed in, these kwargs are ignored). If you want to search for a foreign key field, join
        the foreign key table and field by a '__' i.e. .list(manufacturer__name='Intel') or for
        multiple values i.e. .list(manufacturer__name=['Intel', 'AMD'])

        Examples: 
        from csgapi import client
        cli = client.CSGenome()
        # Filter for multiple values: #
        # find all systems with monikers Sequoia OR Mustang
        cli.systems.list(moniker=['Sequoia', 'Mustang'], exact=True) 

        # Filter using inequalities #
        from csgapi.base import ge, lt, Range
        cli.processors.list(clock_speed=ge(3000)) # Get all processors with clock speeds >= 3000 MHz
        # Get all processors with clock speeds that are 2100 MHz <= clock speed < 2500 MHz
        cli.processors.list(clock_speed=[ge(2100), lt(2500)]) 
        # Get all processors with clock speeds that are 100 MHz <= clock speed <= 1000 MHz 
        # (short hand for a list of ge() and le())
        cli.processors.list(clock_speed=Range(100, 1000)]) 

        Returns:
            A list containing RESTObjects that correspond to all records that matched the search

        Raises:
            CSGError if there was some server error
        """
        # gen can raise CSGError, so this will propogate
        if limit:
            try:
                gen = self.gen(dictionary=dictionary, columns=columns, exact=exact, order_by=order_by, **kwargs)
                result = []
                for _ in range(limit):
                    result.append(next(gen))
            except StopIteration:
                pass  # the limit specified was more than the number of records that match the search

            return result

        # else, limit is not specified so just return all records
        # no error, so error? is False
        return list(self.gen(dictionary=dictionary, columns=columns, exact=exact, order_by=order_by, **kwargs))

    def list_first(self, dictionary: Dict[str, Any] = None, columns: str | List[str] = None, exact=False,
                   order_by: str | Order | List[str | Order] = None,
                   report_count=False, **kwargs) -> Optional[APIObject] | Tuple[Optional[APIObject], int]:
        """
        Return a single object that matches provided properties
        You can pass in a dictionary containing key value pairs to search and filter records by,
        or use keyword parameters as key value pairs instead. In order to search for multiple values
        for a field, you can supply a list of values. Example below. In order to search for a numeric 
        or date column by an inequality, use the gt(), ge(), lt(), le(), or Range() functions from
        csgapi.base. Example also below.
        Kwargs:
            exact: True/False (default False)
                If exact, then string fields are case sensitive
            report_count: True/False (default False)
               If true, then returns a tuple (obj, count) where count is the number of records in 
               table that matched the specified search parameters. In order to search for multiple 
               values for a field, you can supply a list of values. Example below.
            columns: List[str] | str
                Columns of the table to include in the search. If including a single column in 
                search, you can use a string or a list of string columns to include multiple
            order_by: str | csgapi.base.Order | List[str | csgapi.base.Order]
                Orders the search by the str column provided, or if a list, then by all the columns
                in the order they are in the list. In order to order a column by descending order, 
                provice a csgapi.base.desc(column_name). Default ordering is ascending order,
                but you can provide a csgapi.base.asc(column_name) to make it clear to reviewers.
                csgapi.base.desc and csgapi.base.asc are csgapi.base.Order classes.
        **kwargs: values for columns of the table you want to search for (if a dictionary if
        passed in, these kwargs are ignored). If you want to search for a foreign key field, join
        the foreign key table and field by a '__' i.e. .list(manufacturer__name='Intel') or for
        multiple values i.e. .list(manufacturer__name=['Intel', 'AMD'])

        Examples: 
        from csgapi import client
        cli = client.CSGenome()
        # Filter for multiple values: #
        # find first system with monikers Sequoia OR Mustang
        system = cli.systems.list_first(moniker=['Sequoia', 'Mustang'], exact=True) 

        # Filter using inequalities #
        from csgapi.base import ge, lt, Range
        processor = cli.processors.list_first(clock_speed=ge(3000)) # Get first processor with clock speeds >= 3000 MHz
        # Get first processor with clock speeds that are 2100 MHz <= clock speed < 2500 MHz
        processor = cli.processors.list_first(clock_speed=[ge(2100), lt(2500)]) 
        # Get first processor with clock speeds that are 100 MHz <= clock speed <= 1000 MHz 
        # (short hand for a list of ge() and le())
        processor = cli.processors.list_first(clock_speed=Range(100, 1000)]) 

        Returns:
            The first record in the table according to the search parameters as a csgapi.base.RESTObject. 
            If report_count is True, then a tuple (object, count) is returned where count is the total number
            of records that matched the searched parameters.
            If no records were returned by the search, then None is returned in place of the RESTObject.

        Raises:
            CSGError if there was some server error
        """
        query_param = self._parse_params(dictionary or kwargs, columns=columns,
                                         exact=exact, order_by=order_by)

        obj, error = self.csgenome.http_list(self._path, query_param)
        if error:
            raise CSGError(obj)
        if report_count:
            return (self._obj_cls(self, obj[0]), len(obj)) if obj else (None, 0)
        return self._obj_cls(self, obj[0]) if obj else None

    def _parse_params(self, params: Dict[str, Any] = None, columns: List[str] | str = None, exact=False,
                      order_by: str | Order | List[str | Order] = None) -> Dict[str, str]:
        """
        Parses params dictionary for filter as well as specified columns, exact mode, order_by, and desc options 
        and returns a dictionary containing the formatted options
        """
        result = {}

        if columns:
            # add column parameter to result, which can either be in form
            # 'column': 'single_col'   OR
            # 'column': ['list', 'of', 'cols']
            result['columns'] = ','.join(columns) if isinstance(columns, list) else str(columns)

        if exact:
            result['filter_mode'] = 'exact'

        if order_by:
            def parse_column(col: str | Order) -> str:
                parsed_column = col._create_filter() if isinstance(col, Order) else col
                # if used '__' to order by foreign key, replace this with a '.' since that is what API uses
                return parsed_column.replace('__', '.')

            result['order_by'] = ','.join(map(parse_column, order_by)) if isinstance(
                order_by, list) else parse_column(order_by)

        # create filter if specified
        list_of_filters = []
        for k, v in params.items():
            k = k.replace('__', '.')  # for foreign key fields

            if v is None:
                continue

            # single inequality
            if isinstance(v, Inequality):
                list_of_filters.append(f'{k}:{v._create_filter()}')
            # list of inequalities
            elif isinstance(v, list) and all(isinstance(elem, Inequality) for elem in v):
                list_of_filters.append(f'{k}:{",".join(map(lambda elem: elem._create_filter(), v))}')
            # regular filter
            else:
                value = '|'.join(v) if isinstance(v, list) else v
                list_of_filters.append(f'{k}:{value}')

        if list_of_filters:
            result['filter'] = ';'.join(list_of_filters)

        # strip string values of leading and trailing white space
        for k, v in result.items():
            result[k] = v.strip()

        return result

    def gen(self, dictionary: Dict[str, Any] = None, columns: str | List[str] = None, exact=False,
            order_by: str | Order | List[str | Order] = None, **kwargs) -> Generator[APIObject, None, None]:
        """
        Returns a generator where when called with next() will yield the next record
        in the table used.
        You can pass in a dictionary containing key value pairs to search and filter records by,
        or use keyword parameters as key value pairs instead. In order to search for multiple 
        values for a field, you can supply a list of values. Example below. In order to search for a 
        numeric or date column by an inequality, use the gt(), ge(), lt(), le(), or Range() functions 
        from csgapi.base. Example also below.
        Kwargs:
            exact: True/False (default False)
                If exact, then string fields are case sensitive
            columns: List[str] | str
                Columns of the table to include in the search. If including a single column in 
                search, you can use a string or a list of string columns to include multiple
            order_by: str | csgapi.base.Order | List[str | csgapi.base.Order]
                Orders the search by the str column provided, or if a list, then by all the columns
                in the order they are in the list. In order to order a column by descending order, 
                provice a csgapi.base.desc(column_name). Default ordering is ascending order,
                but you can provide a csgapi.base.asc(column_name) to make it clear to reviewers.
                csgapi.base.desc and csgapi.base.asc are csgapi.base.Order classes.
        **kwargs: values for columns of the table you want to search for (if a dictionary if
        passed in, these kwargs are ignored). If you want to search for a foreign key field, join
        the foreign key table and field by a '__' i.e. .gen(manufacturer__name='Intel') or for 
        multiple values i.e. .gen(manufacturer__name=['Intel', 'AMD'])

        Examples: 
        from csgapi import client
        cli = client.CSGenome()
        # Filter for multiple values: #
        # Get generator of systems with a search of monikers Sequoia OR Mustang
        cli.systems.gen(moniker=['Sequoia', 'Mustang'], exact=True) 

        # Filter using inequalities #
        from csgapi.base import ge, lt, Range
        # Get generator of systems with a search of clock speeds >= 3000 MHz
        cli.processors.gen(clock_speed=ge(3000)) 
        # Get generator of systems with a search of clock speeds that are 2100 MHz <= clock speed < 2500 MHz
        cli.processors.gen(clock_speed=[ge(2100), lt(2500)]) 
        # Get generator of systems with a search of clock speeds that are 100 MHz <= clock speed <= 1000 MHz 
        # (short hand for a list of ge() and le())
        cli.processors.gen(clock_speed=Range(100, 1000)]) 

        Returns:
            A generator for the table
        Raises:
            CSGError if there was some server error when called with next()
        """
        query_param = self._parse_params(dictionary or kwargs, columns=columns,
                                         exact=exact, order_by=order_by)

        # set page and limit to be 1 and 50, regardless of what user requested
        query_param['page'] = 1
        query_param['limit'] = 50

        csg_list = CSGList(self.csgenome, self._path, query_data=query_param)

        return csg_list.gen(lambda item: self._obj_cls(self, item, created_from_list=True))


class CreateMixin(_RestManagerBase):
    _path: Optional[str]
    csgenome: CSGenome

    def _check_missing_create_attrs(self, data: Dict):
        missing = []
        for attr in self._create_attrs.required:  # passed in from obj
            if attr not in data:
                missing.append(attr)
        if missing:
            raise CSGError({"errors": f"Missing attributes: {', '.join(missing)}", "status": 400})

    def create(self, data: Dict[str, Any] = None, return_response=False) -> Dict:
        """Create a new object.

        Args:
            data: parameters to send to the server to create the
                         resource
            return_response: If true, return the entire response body 
                         dictionary instead of just the data on success 
                         (default False)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A dictionary containing server data on success and error
            information on failure 

        Raises:
            CSGError if there was some error
        """
        data = data or {}

        self._check_missing_create_attrs(data)

        path = self._path  # NOTE: might not be necessary, consider

        data = {k: v for k, v in data.items() if v is not None}
        server_data = self.csgenome.http_post(path, post_data=data)
        
        if 'errors' in server_data:
            raise CSGError(server_data)

        elif 'status' in server_data and not str(server_data['status']).startswith('2'):
            server_data['errors'] = 'Error with creation'
            raise CSGError(server_data)

        elif return_response:
            return server_data
        else:
            return server_data['data']


class UpdateMixin(_RestManagerBase):
    _computed_path: Optional[str]
    _from_parent_attrs: Dict[str, Any]
    _obj_cls: Optional[Type[base.RESTObject]]
    _parent: Optional[base.RESTObject]
    _parent_attrs: Dict[str, Any]
    _path: Optional[str]
    _update_uses_post: bool = False
    csgenome: CSGenome

    def _check_missing_update_attrs(self, data: Dict):
        # Remove the id field from the required list as it was previously moved
        # to the http path.
        required = tuple(
            [k for k in self._update_attrs.required if k != self._obj_cls._id_attr]
        )
        missing = []
        for attr in required:
            if attr not in data:
                missing.append(attr)
        if missing:
            raise CSGError({"errors": f"Missing attributes: {', '.join(missing)}", "status": 400})

    def update(self, uid: int, new_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update an object on the server.

        Args:
            uid: ID of the object to update
            new_data: the update data for the object
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The server response as a Dict

        Raises:
            CSGError if there was some error
        """
        new_data = new_data or {}

        if uid is None:
            raise CSGError({"errors": "uid not specified", "status": 400})
        else:
            path = f"{self._path}/{uid}"

        self._check_missing_update_attrs(new_data)

        server_data = self.csgenome.http_put(path, put_data=new_data)

        if 'data' in server_data.keys():
            res = server_data['data']
            return res
        else:
            if 'errors' not in server_data:
                server_data['errors'] = "Error updating record"
            raise CSGError(server_data)


class DeleteMixin(_RestManagerBase):
    _path: Optional[str]
    csgenome: CSGenome

    def delete(self, uid: int) -> APIObject:
        """Delete an object on the server.

        Args:
            uid: ID of the object to delete
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns: The RESTObject of the record that was deleted

        Raises:
            CSGError if there was some error
        """
        if uid is None:
            raise CSGError({"errors": "uid not specified", "status": 400})
        else:
            path = f"{self._path}/{uid}"
        server_data = self.csgenome.http_delete(path)
        data = server_data['data'] if 'data' in server_data else server_data
        return self._obj_cls(self, data)
