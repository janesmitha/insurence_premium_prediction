from insurance_premium.constant import COLUMN_REGION, COLUMN_SEX, COLUMN_SMOKER, DATASET_SCHEMA_COLUMNS_KEY, DOMAIN_VALUES_COLUMN_KEY
from insurance_premium.logger import logging
from insurance_premium.exception import InsurancePremiumExcecption
from insurance_premium.entity.config_entity import DataValidationConfig
from insurance_premium.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
import os,sys
import pandas  as pd
# from evidently.model_profile.sections import DataDriftProfileSection
# from evidently.model_profile import Profile
# from evidently.dashboard.tabs import DataDriftTab
import json
from insurance_premium.util.util import read_yaml_file
from insurance_premium import*

class DataValidation:
    

    def __init__(self, data_validation_config:DataValidationConfig,
        data_ingestion_artifact:DataIngestionArtifact):
        try:
            logging.info(f"{'>>'*30}Data Valdaition log started.{'<<'*30} \n\n")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_schema_info = read_yaml_file(self.data_validation_config.schema_file_path)
        except Exception as e:
            raise InsurancePremiumExcecption(e,sys) from e


    def get_train_and_test_df(self):
        try:
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df,test_df
        except Exception as e:
            raise InsurancePremiumExcecption(e,sys) from e


    def is_train_test_file_exists(self)->bool:
        try:
            logging.info("Checking if training and test file is available")
            is_train_file_exist = False
            is_test_file_exist = False

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            is_train_file_exist = os.path.exists(train_file_path)
            is_test_file_exist = os.path.exists(test_file_path)

            is_available =  is_train_file_exist and is_test_file_exist

            logging.info(f"Is train and test file exists?-> {is_available}")
            
            if not is_available:
                training_file = self.data_ingestion_artifact.train_file_path
                testing_file = self.data_ingestion_artifact.test_file_path
                message=f"Training file: {training_file} or Testing file: {testing_file}" \
                    "is not present"
                raise Exception(message)

            return is_available

        except Exception as e:
            raise InsurancePremiumExcecption(e,sys) from e

    
    def validate_dataset_schema(self)->bool:
        

            #validate training and testing dataset using schema file
            #1. Number of Column
            #2. Check the value of domain values
            #   sex:
            #     - male
            #     - female

            #   region:
            #     - northeast
            #     - northwest
            #     - southeast
            #     - southwest
            
            #   smoker:
            #     - yes
            #     - no
            #3. Check column names
        try:
            validation_status = False

            train_df, test_df = self.get_train_and_test_df()
            dataset_schema_info = self.data_validation_schema_info[DATASET_SCHEMA_COLUMNS_KEY]
            domain_values_info = self.data_validation_schema_info[DOMAIN_VALUES_COLUMN_KEY]
            dataset_columns_name = set(dataset_schema_info.keys())
            train_columns_name = set(train_df.columns)
            test_columns_name = set(test_df.columns)
            data_set_column_number = len(dataset_columns_name)
            train_column_number = len(train_columns_name)
            test_column_number = len(test_columns_name)

            sex_domain_value = set(domain_values_info[COLUMN_SEX])
            region_domain_value = set(domain_values_info[COLUMN_REGION])
            smoker_domain_value = set(domain_values_info[COLUMN_SMOKER])

            train_domain_value_sex = set(train_df[COLUMN_SEX].unique())
            train_domain_value_region = set(train_df[COLUMN_REGION].unique())
            train_domain_value_smoker = set(train_df[COLUMN_SMOKER].unique())

            test_domain_value_sex = set(test_df[COLUMN_SEX].unique())
            test_domain_value_region = set(test_df[COLUMN_REGION].unique())
            test_domain_value_smoker = set(test_df[COLUMN_SMOKER].unique())

            if (train_column_number == data_set_column_number) and (test_column_number == data_set_column_number):
                if (train_columns_name == dataset_columns_name) and (test_columns_name == dataset_columns_name):
                    if (train_domain_value_sex == sex_domain_value) and (test_domain_value_sex == sex_domain_value):
                        if (train_domain_value_region == region_domain_value) and (test_domain_value_region == region_domain_value):
                            if (train_domain_value_smoker == smoker_domain_value) and (test_domain_value_smoker == smoker_domain_value):
                                validation_status = True
            else:
                pass
            return validation_status

        except Exception as e:
            raise InsurancePremiumExcecption(e,sys) from e

    # def get_and_save_data_drift_report(self):
    #     try:
    #         profile = Profile(sections=[DataDriftProfileSection()])

    #         train_df,test_df = self.get_train_and_test_df()

    #         profile.calculate(train_df,test_df)

    #         report = json.loads(profile.json())

    #         report_file_path = self.data_validation_config.report_file_path
    #         report_dir = os.path.dirname(report_file_path)
    #         os.makedirs(report_dir,exist_ok=True)

    #         with open(report_file_path,"w") as report_file:
    #             json.dump(report, report_file, indent=6)
    #         return report
    #     except Exception as e:
    #         raise InsurancePremiumExcecption(e,sys) from e

    # def save_data_drift_report_page(self):
    #     try:
    #         dashboard = Dashboard(tabs=[DataDriftTab()])
    #         train_df,test_df = self.get_train_and_test_df()
    #         dashboard.calculate(train_df,test_df)

    #         report_page_file_path = self.data_validation_config.report_page_file_path
    #         report_page_dir = os.path.dirname(report_page_file_path)
    #         os.makedirs(report_page_dir,exist_ok=True)

    #         dashboard.save(report_page_file_path)
    #     except Exception as e:
    #         raise InsurancePremiumExcecption(e,sys) from e

    # def is_data_drift_found(self)->bool:
    #     try:
    #         report = self.get_and_save_data_drift_report()
    #         self.save_data_drift_report_page()
    #         return True
    #     except Exception as e:
    #         raise InsurancePremiumExcecption(e,sys) from e

    def initiate_data_validation(self)->DataValidationArtifact :
        try:
            self.is_train_test_file_exists()
            self.validate_dataset_schema()
            # self.is_data_drift_found()

            data_validation_artifact = DataValidationArtifact(
                schema_file_path=self.data_validation_config.schema_file_path,
                report_file_path=self.data_validation_config.report_file_path,
                report_page_file_path=self.data_validation_config.report_page_file_path,
                is_validated=True,
                message="Data Validation performed successully."
            )
            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise InsurancePremiumExcecption(e,sys) from e


    def __del__(self):
        logging.info(f"{'>>'*30}Data Valdaition log completed.{'<<'*30} \n\n")
        



                            