
from Dashboards.Dashboards import Dashboards
from NikeCA import Snowflake


class InclusionExclusion(Dashboards, Snowflake):

    def __init__(self, username, warehouse, role, database):
        super().__init__(username=username, warehouse=warehouse, role=role, database=database)

        self.username = username
        self.warehouse = warehouse
        self.role = role
        self.database = database

    def pos_data_quality_review(self
                                , username: str | None = None
                                , warehouse: str | None = None
                                , database: str | None = None
                                , role: str | None = None
                                , columns: list | None = None
                                , filters: list | None = None
                                , order_by: list | None = None
                                , polars: bool = False
                                , start_date: str | None = None
                                , end_date: str | None = None):

        """
            Perform a data quality review on the point of sale (POS) data.

            Args:
                username (str | None): The username. If None, the value will be taken from `self.username`.
                warehouse (str | None): The warehouse. If None, the value will be taken from `self.warehouse`.
                database (str | None): The database. If None, the value will be taken from `self.database`.
                role (str | None): The role. If None, the value will be taken from `self.role`.
                columns (list | None): The columns to select from the data. If None, the default columns will be used.
                filters (list | None): The filters to apply to the data. If None, no filters will be applied.
                order_by (list | None): The columns to order the data by. If None, the default order will be used.
                polars (bool): Whether to use polars for data manipulation. Default is False.
                start_date (str | None): The start date. If None, no start date is used.
                end_date (str | None): The end date. If None, no end date is used.

            Returns:
                Union[pl.DataFrame, pd.DataFrame]: The filtered POS data based on the specified parameters.

            Raises:
                TypeError: If `columns` is not a list.
                TypeError: If `filters` is not a list.
                TypeError: If `order_by` is not a list.

            Examples:
                # Perform a data quality review on POS data for the default user and settings
                >>> obj = YourClassName()
                >>> result = obj.pos_data_quality_review()
                >>> result # doctest: +ELLIPSIS
                    ...     | ...    | ...
                    ...     | ...    | ...
                ...

                # Perform a data quality review on POS data for a specific user and settings
                >>> result = obj.pos_data_quality_review(username='john', warehouse='wh1', database='db1', role='admin',
                ...                                      columns=['col1', 'col2'], filters=['col3 > 0'], order_by=['col1'])
                >>> result # doctest: +ELLIPSIS
                    ...     | ...    | ...
                    ...     | ...    | ...
                ...
            """

        if username is None:
            username = self.username
        if warehouse is None:
            warehouse = self.warehouse
        if database is None:
            database = self.database
        if role is None:
            role = self.role

        import polars as pl
        import datetime
        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        table = config['inclusion_exclusion_pos_data_quality_review'].get('table')
        a = config['inclusion_exclusion_summary_and_home'].get('col_a')

        # Ensure columns is a list
        if not (isinstance(columns, list) or columns is None):
            raise TypeError("columns must be a list")

        # Ensure filters is a list
        if not (isinstance(filters, list) or filters is None):
            raise TypeError("filters must be a list")

        # Ensure order_by is a list
        if not (isinstance(order_by, list) or order_by is None):
            raise TypeError("order_by must be a list")

        if columns is None:
            columns_str = config['inclusion_exclusion_pos_data_quality_review'].get('columns')
        else:
            columns_str = ', '.join(columns)

        if filters is None:
            filters = []
        # Join column filters into comma-separated string, if any
        if len(filters) > 0:
            filters_str = 'AND '.join(filters)
            filters_str = f'WHERE {filters_str}'
        else:
            filters_str = ''

        if order_by is None:
            order_by = config['inclusion_exclusion_pos_data_quality_review'].get('order_by')
        else:
            order_by = ', '.join(order_by)

        query = f"""
            SELECT
                {columns_str}

            FROM
                {table}
            {filters_str}

            ORDER BY
                {order_by}

            ;
        """

        df = Snowflake(username=username, warehouse=warehouse, database=database, role=role)\
            .snowflake_pull(query=query, polars=polars)

        if start_date is None and end_date is None:
            if polars:
                return df.filter(pl.col(a) == pl.col(a).max())
            else:
                return df.filter(pl.col(a) == pl.col(a).max()).to_pandas()
        elif end_date is None:
            if polars:
                return df.filter((pl.col(a) >= datetime.datetime.strptime(start_date, '%Y-%m-%d')))
            else:
                return df.filter((pl.col(a) >= datetime.datetime.strptime(start_date, '%Y-%m-%d'))).to_pandas()
        elif start_date is None:
            if polars:
                return df.filter((pl.col(a) <= datetime.datetime.strptime(end_date, '%Y-%m-%d')))
            else:
                return df.filter((pl.col(a) <= datetime.datetime.strptime(end_date, '%Y-%m-%d'))).to_pandas()
        else:
            df = df.filter((pl.col(a) >= datetime.datetime.strptime(start_date, '%Y-%m-%d')))
            if polars:
                return df.filter((pl.col(a) <= datetime.datetime.strptime(end_date, '%Y-%m-%d')))
            else:
                return df.filter((pl.col(a) <= datetime.datetime.strptime(end_date, '%Y-%m-%d'))).to_pandas()

    def summary(self
                , username: str | None = None
                , warehouse: str | None = None
                , database: str | None = None
                , role: str | None = None
                , columns=None
                , filters=None
                , order_by=None
                , polars: bool = True
                , start_date: str | None = None
                , end_date: str | None = None
                ):

        """
            Generate a summary based on specified parameters.

            Args:
                username (str | None): The username. If None, the value will be taken from `self.username`.
                warehouse (str | None): The warehouse. If None, the value will be taken from `self.warehouse`.
                database (str | None): The database. If None, the value will be taken from `self.database`.
                role (str | None): The role. If None, the value will be taken from `self.role`.
                columns: The columns to select from the data.
                filters: The filters to apply to the data.
                order_by: The column to order the data by.
                polars (bool): Whether to use polars for data manipulation. Default is True.
                start_date (str | None): The start date. If None, no start date is used.
                end_date (str | None): The end date. If None, no end date is used.

            Returns:
                Union[pd.DataFrame, pl.DataFrame]: The summary data.

            Examples:
                # Generate a summary for the default user and settings
                >>> obj = YourClassName()
                >>> result = obj.summary()
                >>> result # doctest: +ELLIPSIS
                  RETAILERS | INCLUDED | PERCENT_INCLUDED | EXCLUDED | PERCENT_EXCLUDED
                ...         | ...      | ...              | ...      | ...
                ...

                # Generate a summary for a specific user and settings
                >>> result = obj.summary(username='john', warehouse='wh1', database='db1', role='admin',
                ...                      start_date='2023-01-01', end_date='2023-05-01')
                >>> result # doctest: +ELLIPSIS
                  RETAILERS | INCLUDED | PERCENT_INCLUDED | EXCLUDED | PERCENT_EXCLUDED
                ...         | ...      | ...              | ...      | ...
                ...
            """

        if username is None:
            username = self.username
        if warehouse is None:
            warehouse = self.warehouse
        if database is None:
            database = self.database
        if role is None:
            role = self.role


        import polars as pl
        import pandas as pd
        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        a = config['inclusion_exclusion_summary_and_home'].get('col_a')
        b = config['inclusion_exclusion_summary_and_home'].get('col_b')
        c = config['inclusion_exclusion_summary_and_home'].get('col_c')

        df = InclusionExclusion.pos_data_quality_review(self, username=username, warehouse=warehouse,
                                                        database=database, role=role, columns=columns, filters=filters,
                                                        order_by=order_by, polars=polars, start_date=start_date,
                                                        end_date=end_date)

        df_pd = pd.DataFrame()

        df_pd['RETAILERS'] = df.select(pl.col(b).count()).to_arrow()[0]

        df_pd['INCLUDED'] = df.select(df.filter(pl.col(c) == 'Y').select(pl.col(b).count())).to_arrow()[0]
        df_pd['PERCENT_INCLUDED'] = f"{str(round(df_pd['INCLUDED' ] /df_pd['RETAILERS' ] *100, 0))}%"
        df_pd['EXCLUDED'] = df.select(df.filter(pl.col(c) == 'N').select(pl.col(b).count())).to_arrow()[0]
        df_pd['PERCENT_EXCLUDED'] = f"{str(round(df_pd['EXCLUDED' ] /df_pd['RETAILERS'] * 100, 0))}%"

        if polars:
            return pl.DataFrame(df_pd)
        return df_pd

    def home_summary(self
                     , username: str | None = None
                     , warehouse: str | None = None
                     , database: str | None = None
                     , role: str | None = None
                     , columns=None
                     , filters=None
                     , order_by=None
                     , polars: bool = True
                     , start_date: str | None = None
                     , end_date: str | None = None
                     ):
        """
        Generate a summary of home data.

        Args:
            username (str | None): The username. If None, the value will be taken from `self.username`.
            warehouse (str | None): The warehouse. If None, the value will be taken from `self.warehouse`.
            database (str | None): The database. If None, the value will be taken from `self.database`.
            role (str | None): The role. If None, the value will be taken from `self.role`.
            columns: The columns to select from the data.
            filters: The filters to apply to the data.
            order_by: The column to order the data by.
            polars (bool): Whether to use polars for data manipulation. Default is True.
            start_date (str | None): The start date. If None, no start date is used.
            end_date (str | None): The end date. If None, no end date is used.

        Returns:
            pl.DataFrame: The summary data.

        Examples:
            # Generate a summary for the default user and settings
            >>> obj = YourClassName()
            >>> result = obj.home_summary()
            >>> result # doctest: +ELLIPSIS
            col_h  | Total Retailers | INCLUDED | EXCLUDED | SALE AVLB | SALE UNAVLB | SALE IN TREND | SALE NOT IN TREND | INV IN TREND | INV NOT IN TREND | % INCLUDED | % EXCLUDED | % Retailers Sales Available | % Retailers Sales Unavailable | % SALE IN TREND | % SALE NOT IN TREND | % INV IN TREND | % INV NOT IN TREND
            ...     | ...             | ...      | ...      | ...       | ...         | ...           | ...               | ...          | ...              | ...        | ...         | ...                        | ...                          | ...             | ...                 | ...            | ...
            ...

            # Generate a summary for a specific user and settings
            >>> result = obj.home_summary(username='john', warehouse='wh1', database='db1', role='admin',
            ...                           start_date='2023-01-01', end_date='2023-05-01')
            >>> result # doctest: +ELLIPSIS
            col_h  | Total Retailers | INCLUDED | EXCLUDED | SALE AVLB | SALE UNAVLB | SALE IN TREND | SALE NOT IN TREND | INV IN TREND | INV NOT IN TREND | % INCLUDED | % EXCLUDED | % Retailers Sales Available | % Retailers Sales Unavailable | % SALE IN TREND | % SALE NOT IN TREND | % INV IN TREND | % INV NOT IN TREND
            ...     | ...             | ...      | ...      | ...       | ...         | ...           | ...               | ...          | ...              | ...        | ...         | ...                        | ...                          | ...             | ...                 | ...            | ...
            ...
        """

        if username is None:
            username = self.username
        if warehouse is None:
            warehouse = self.warehouse
        if database is None:
            database = self.database
        if role is None:
            role = self.role

        import datetime

        import polars as pl
        import configparser

        config = configparser.ConfigParser()
        config.read('pip.ini')

        a = config['inclusion_exclusion_summary_and_home'].get('col_a')
        b = config['inclusion_exclusion_summary_and_home'].get('col_b')
        c = config['inclusion_exclusion_summary_and_home'].get('col_c')
        d = config['inclusion_exclusion_summary_and_home'].get('col_d')
        e = config['inclusion_exclusion_summary_and_home'].get('col_e')
        f = config['inclusion_exclusion_summary_and_home'].get('col_f')
        g = config['inclusion_exclusion_summary_and_home'].get('col_g')
        h = config['inclusion_exclusion_summary_and_home'].get('col_h')

        df = InclusionExclusion.pos_data_quality_review(self, username=username, warehouse=warehouse, database=database,
                                                        role=role, columns=columns, filters=filters, order_by=order_by,
                                                        polars=polars, start_date=start_date, end_date=end_date)
        df_count = (
            df
            .with_columns([
                pl.col(c).count().over([
                    d
                ]).alias('Total Retailers')
                , pl.col(c).filter(
                    pl.col(c) == 'Y'
                ).count().over(d).alias('INCLUDED')
                , pl.col(c).filter(
                    pl.col(c) == 'N'
                ).count().over(d).alias('EXCLUDED')
                , pl.col(e).filter(
                    pl.col(e) == 'Y'
                ).count().over(d).alias('SALE AVLB')
                , pl.col(e).filter(
                    pl.col(e) == 'N'
                ).count().over(d).alias('SALE UNAVLB')
                , pl.col(f).filter(
                    pl.col(f) == 'Y'
                ).count().over(d).alias('SALE IN TREND')
                , pl.col(f).filter(
                    pl.col(f) == 'N'
                ).count().over(d).alias('SALE NOT IN TREND')
                , pl.col(g).filter(
                    pl.col(g) == 'Y'
                ).count().over(d).alias('INV IN TREND')
                , pl.col(g).filter(
                    pl.col(g) == 'N'
                ).count().over(d).alias('INV NOT IN TREND')


            ])
        ).select([h, 'Total Retailers', 'INCLUDED', 'EXCLUDED', 'SALE AVLB', 'SALE UNAVLB',
                  'SALE IN TREND', 'SALE NOT IN TREND', 'INV IN TREND', 'INV NOT IN TREND']).unique()

        df_count = (df_count
                    .lazy()
                    .with_columns([
            (pl.col('INCLUDED') / pl.col('Total Retailers') * 100).round(0).alias('% INCLUDED')
            , (pl.col('EXCLUDED') / pl.col('Total Retailers') * 100).round(0).alias('% EXCLUDED')
            , (pl.col('SALE AVLB') / pl.col('Total Retailers') * 100).round(0).alias('% Retailers Sales Available')
            , (pl.col('SALE UNAVLB') / pl.col('Total Retailers') * 100).round(0).alias('% Retailers Sales Unavailable')
            , (pl.col('SALE IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% SALE IN TREND')
            , (pl.col('SALE NOT IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% SALE NOT IN TREND')
            , (pl.col('INV IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% INV IN TREND')
            , (pl.col('INV NOT IN TREND') / pl.col('Total Retailers') * 100).round(0).alias('% INV NOT IN TREND')

        ]).collect()
                    )

        return df_count




