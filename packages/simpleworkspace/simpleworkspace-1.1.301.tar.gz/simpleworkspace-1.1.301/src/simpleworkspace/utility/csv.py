
class CSVReader:
    '''
    Simple csv reader and writer wrapper class. The class can also be used to create new csv files.

    Properties for the user:
    * self.Delimiter: The delimiter to be used when loading or exporting a csv file. It is specified in the constructor but can be freely changed.
    * self.Rows     : A 2D list of csv rows in the format Rows[row][col]. It can be manipulated to alter the exported csv file on Save().
    * self.Headers  : A list of column names that must match the column count on the rest of csv rows.
                      When headers is None or an empty list, the exported csv file will not include a header row.
    '''

    def __init__(self, delimiter:str=',') -> None:
        self.Delimiter = delimiter
        '''The delimiter character to use'''
        self.Rows = [] #type: list[list[str]]
        '''contains the a 2d list of data rows, self.Rows[row][col]'''
        self.Headers = [] #type: list[str]
        '''list of column names aka headers'''
        return
        

    def Load(self, filepath:str, hasHeader=True):
        '''Imports a csv instance from a file'''
        import csv

        self.Rows = []
        self.Headers = []
        with open(filepath, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.Delimiter)
            if(hasHeader):
                self.Headers = next(reader)
            for row in reader:
                self.Rows.append(row)
        return
    
    def Save(self, filepath:str):
        '''Exports the csv instance out to a filepath'''
        import csv

        with open(filepath, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=self.Delimiter)
            if(self.Headers):
                csv_writer.writerow(self.Headers)
            csv_writer.writerows(self.Rows)
        pass
    