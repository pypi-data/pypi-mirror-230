from pyPhasesRecordloaderSHHS.recordLoaders.RecordLoaderSHHS import RecordLoaderSHHS
from pyPhasesRecordloader.recordLoaders.CSVMetaLoader import CSVMetaLoader

class RecordLoaderMESA(RecordLoaderSHHS):
    def getFilePathSignal(self, recordId):
        return f"{self.filePath}/polysomnography/edfs/{recordId}.edf"

    def getFilePathAnnotation(self, recordId):
        return f"{self.filePath}/polysomnography/annotations-events-nsrr/{recordId}-nsrr.xml"

        
    def getMetaData(self, recordName):
        metaData = super().getMetaData(recordName, loadMetadataFromCSV=False)
        metaData["recordId"] = recordName
        relevantRows_harmonized = {
            "age": "nsrr_age",
            "gender": "nsrr_sex",
            "tst": "nsrr_ttldursp_f1",
            "ahi": "nsrr_ahi_hp4r",
            "indexArousal": "nsrr_phrnumar_f1",
            "race": "nsrr_race",
        }
        relevantRows = {
            # "gender": "gender1",
            # "age": "sleepage5c",
            "sLatency": "slp_lat5",
            "rLatency": "rem_lat15",
            "waso": "waso5",
            "sEfficiency": "slp_eff5",
            "indexPlms": "avgplm5",
            "indexPlmsArousal": "avgplma5",
            # for countArousal
            "arnrembp5": "arnrembp5",
            "arnremop5": "arnremop5",
            "arrembp5": "arrembp5",
            "arremop5": "arremop5",
            # therapy / diagnostics
            # % N1, N2, N3, R
            # not existing
            #"bmi
        }
        csvLoader = CSVMetaLoader(
            f"{self.filePath}/mesa-sleep-dataset-0.5.0 (1).csv", idColumn="mesaid", relevantRows=relevantRows
        )
        csvMetaData = csvLoader.getMetaData(int(recordName[11:]))
        metaData.update(csvMetaData)
        
        csvLoader = CSVMetaLoader(
            f"{self.filePath}/mesa-sleep-harmonized-dataset-0.5.0 (1).csv", idColumn="mesaid", relevantRows=relevantRows_harmonized
        )
        csvMetaData = csvLoader.getMetaData(int(recordName[11:]))
        metaData.update(csvMetaData)

        metaData["countArousal"] = metaData["arnrembp5"] + metaData["arnremop5"] + metaData["arremop5"] + metaData["arrembp5"]

        return metaData