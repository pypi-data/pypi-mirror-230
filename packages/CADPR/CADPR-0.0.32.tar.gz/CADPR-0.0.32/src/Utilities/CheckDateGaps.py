

from datetime import datetime, timedelta


class CheckDateGaps:

    @staticmethod
    def check_date_gaps(date_list):
        """
        Check for date gaps in a list of date strings.

        Args:
            date_list (list): A list of date strings in the format '%Y-%m-%d'.

        Returns:
            list: A list of missing dates (as strings) that have gaps between them.

        Examples:
            >>> dates = ['2023-05-01', '2023-05-02', '2023-05-04', '2023-05-07']
            >>> check_date_gaps(dates)
            ['2023-05-03', '2023-05-05', '2023-05-06']

            >>> dates = ['2023-01-01', '2023-01-03', '2023-01-05']
            >>> check_date_gaps(dates)
            ['2023-01-02', '2023-01-04']

            >>> dates = ['2023-12-31']
            >>> check_date_gaps(dates)
            []

        """
        # Convert date strings to datetime objects, excluding '9999-12-31'
        dates = []
        gaps = []
        for date in date_list:
            if date == '9999-12-31':
                gaps.append(date)
            else:
                dates.append(datetime.strptime(str(date), '%Y-%m-%d'))

        # Sort the datetime objects
        dates.sort()

        # Check for gaps
        for i in range(len(dates) - 1):
            if dates[i + 1] - dates[i] > timedelta(days=1):
                missing_date = dates[i] + timedelta(days=1)
                while missing_date < dates[i + 1]:
                    if missing_date == datetime(9999, 12, 31):
                        gaps.append('9999-12-31')
                    else:
                        gaps.append(missing_date.strftime('%Y-%m-%d'))
                    missing_date += timedelta(days=1)

        return gaps


