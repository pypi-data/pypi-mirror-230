

class SearchFiles:

    def search_files(self, directory_path: str = None, search_string: str or list = None, save_path: str = None):
        """
        This function will go through a directory and all subdirectories and try to open each file no matter
        if it is another directory, a sql code, hql, or python file, or whatever. It will search for a substring
        or list of substrings within the file. It will then create a Polars dataframe with the following columns
        (Path, Filename, Start, Occurrences, Lines, Context). If the save_path is not None it will save the
        dataframe to the save_path.

        Parameters
        ----------
        directory_path : str
            The directory to recursively search through.
        search_string : str or list
            The substring or the list of substrings is the search criteria.
        save_path : str
            The location where to save the results.

        Returns
        -------
        Polars dataframe
            A Polars dataframe with the following columns (Path, Filename, Start, Occurrences, Lines, Context).
        """

        import os
        import re
        import pandas as pd

        # Check if directory_path is valid
        if not os.path.isdir(directory_path):
            raise ValueError('directory_path is not a valid directory.')

        # Check if search_string is valid
        if not isinstance(search_string, str) and not isinstance(search_string, list):
            raise ValueError('search_string must be a string or a list of strings.')

        if isinstance(search_string, str):
            search_string = [search_string]

        # Initialize the Polars dataframe
        df = {}

        for i in search_string:
            print(i)

            df[i] = {}

            # Recursively search through the directory
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    # Get the relative path for the file
                    path = os.path.relpath(os.path.join(root, file), directory_path)
                    # print(f"Searching:\t{filepath}/{file}")

                    with open(os.path.join(root, file), 'rb') as f:
                        byte_sequence = f.read()  # read the first 100 bytes
                        lines = byte_sequence.decode('iso-8859-1')

                        if re.search(i.upper(),  lines.upper()):
                            filepath = path[path.index('/') + 1:]

                            indexes = []

                            end = '.*\n'
                            line_end_char_number = []
                            for line_char_number in re.finditer(end, lines):
                                line_end_char_number.append(line_char_number.end())

                            df[i][filepath] = {}
                            try:
                                if len(line_end_char_number) == 0:
                                    continue
                                elif len(line_end_char_number) < 10:
                                    df[i][filepath]['StartOfFile'] = lines[:line_end_char_number[len(line_end_char_number) - 1]]

                                else:
                                    df[i][filepath]['StartOfFile'] = lines[:line_end_char_number[9]]
                            except Exception as e:
                                print('Exception occured: ', e)
                                print('continuing')
                                continue
                            df[i][filepath]['Context'] = {}
                            df[i][filepath]['NumberOfOccurrences'] = 0

                            line_number_list = []

                            for index in re.finditer(i.upper(), lines.upper()):
                                indexes.append(index.start())
                                df[i][filepath]['NumberOfOccurrences'] += 1
                                print(f'Found {i} in file {filepath}/{file}')
                                for line_number in line_end_char_number:
                                    if line_number > index.start():
                                        line_number_list.append(line_end_char_number.index(line_number) + 1)
                                        print(f'Line number: {line_end_char_number.index(line_number) + 1}\n\n')
                                        df[i][filepath]['Context'][str(line_end_char_number.index(line_number) + 1)] = lines[index.start() - 100: index.start() + 100]
                                        break
                            df[i][filepath]['LineNumbers'] = line_number_list

            print(i)

        reformed_dict = {}
        for k, v in df.items():
            for x, y in v.items():
                reformed_dict[(k, x)] = y

        df_pd = pd.DataFrame(reformed_dict).T

        df_pd.reset_index(inplace=True)

        df_pd.columns = ['SearchCriteria', 'Filepath', 'StartOfFile', 'Context', 'NumberOfOccurrences', 'LineNumbers']

        df_pd.to_csv(save_path, index=False)

        print(df_pd)

        return df_pd
