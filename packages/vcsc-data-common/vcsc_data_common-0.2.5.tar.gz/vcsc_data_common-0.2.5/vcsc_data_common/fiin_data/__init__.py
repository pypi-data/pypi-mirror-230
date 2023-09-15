from deltalake import DeltaTable
import pyarrow.compute as pc
import pyarrow as pa
import datetime

class FiinDataFetcher():
    def __init__(self, aws_access_key: str, aws_secret_key: str) -> None:
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.table_parent_path = 's3://vietcap-ai/prod/fiin'

    def __fetch_data(self,table_name:str, filter_condition):

        uri = f"{self.table_parent_path}/{table_name}"

        dt = DeltaTable(uri, storage_options={
            "AWS_ACCESS_KEY_ID": self.aws_access_key,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_key,
            'AWS_REGION': "ap-southeast-1"
        })
        print('filter ne')
        print(filter_condition)
        data_set = dt.to_pyarrow_dataset()
        print(data_set)
        print(datetime.datetime.now())

        test_filter = (pc.field('NewsId') == 10833215)
        result = data_set.scanner(filter=filter_condition)

        print( data_set.scanner(filter=filter_condition).count_rows())
        
        print('done scan')
        result = result.to_reader()
        print('done reader')
        result = result.read_pandas()
        print(datetime.datetime.now())
        print(result.sort_values('PublicDate'))
        


    def fetch_stx_msg_NewsVI(self,organ_code:str=None,from_date:str=None):
        
        filter_1 = (pc.field('OrganCode') == organ_code) if organ_code != None else None
        
        filter_2 = (pc.field('UpdateDate') >= pa.scalar(datetime.datetime.strptime(from_date, "%Y-%m-%d"))) if from_date != None else None

        combined_filter = self.combine_filter(filter_1,filter_2)

        self.__fetch_data('stx_msg_NewsVI',combined_filter)

    def combine_filter(self, *argv):
        combined_filters = None
        i = 0
        for arg in argv:
            print(i)
            if(combined_filters.__class__ != None.__class__):

                if(arg.__class__ != None.__class__):
                    combined_filters =  combined_filters & arg
               
            else:
                if(arg.__class__ != None.__class__):
                    combined_filters =  arg

            i+=1

        return combined_filters

        
        