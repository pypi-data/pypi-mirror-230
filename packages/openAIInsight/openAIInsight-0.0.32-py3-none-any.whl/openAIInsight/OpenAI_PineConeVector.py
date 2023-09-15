import json
import openai
import pinecone
import datetime
import traceback
import pandas as pd
from flask import request
import loggerutility as logger
import commonutility as common
from openai.embeddings_utils import get_embedding, get_embeddings, cosine_similarity


class OpenAI_PineConeVector:
    
    index_name          =   "" 
    openAI_apiKey       =   "" 
    pineCone_apiKey     =   "" 
    queryList           =   ""
    dfJson              =   "" 
    engineName          =   "text-embedding-ada-002" # Model that we want to use 
    dimensions          =   1536
    my_index            =   ""
    enterpriseName      =   "" 
    modelScope          =   "E"
    entity_type         =   "" 
    enterpriseEntityInfo=   ""

    def trainData(self, pineCone_json):
        try:
            result = ""
            df     = None

            logger.log("inside PineConeVector class trainData()","0")
            if "openAI_apiKey" in pineCone_json and pineCone_json["openAI_apiKey"] != None:
                self.openAI_apiKey = pineCone_json["openAI_apiKey"]           
                logger.log(f"\n openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
            
            if "pineCone_apiKey" in pineCone_json and pineCone_json["pineCone_apiKey"] != None:
                self.pineCone_apiKey = pineCone_json["pineCone_apiKey"]           
                logger.log(f"\n pineCone_apiKey:::\t{self.pineCone_apiKey} \t{type(self.pineCone_apiKey)}","0")

            if "modelParameter" in pineCone_json and pineCone_json["modelParameter"] != None:
                self.modelParameter = json.loads(pineCone_json['modelParameter'])
            
            if "index_name" in self.modelParameter and self.modelParameter["index_name"] != None:
                self.index_name = self.modelParameter["index_name"]
                logger.log(f"\n index_name:::\t{self.index_name} \t{type(self.index_name)}","0")
            
            if "modelJsonData" in pineCone_json and pineCone_json["modelJsonData"] != None:
                self.dfJson = pineCone_json["modelJsonData"]
                
            if "enterprise" in pineCone_json and pineCone_json["enterprise"] != None:
                self.enterpriseName = pineCone_json["enterprise"]
                logger.log(f"\n enterpriseName :::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            if "modelScope" in pineCone_json and pineCone_json["modelScope"] != None:
                self.modelScope = pineCone_json["modelScope"]
                logger.log(f"\n modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")
            
            if "entity_type" in self.modelParameter and self.modelParameter["entity_type"] != None:
                self.entity_type = self.modelParameter["entity_type"]
                logger.log(f"\nentity_type:::\t{self.entity_type} \t{type(self.entity_type)}","0")
            
            if type(self.dfJson) == str :
                parsed_json = json.loads(self.dfJson)
                if self.index_name == 'item' or self.index_name == 'vision-masters':
                    df = pd.DataFrame(parsed_json[1:])  # Added because actual data values start from '1' position
                    
                elif self.index_name == 'document':
                    df = pd.DataFrame(parsed_json)      # Added because actual data values start from '0' position
            else:
                df = pd.DataFrame(self.dfJson)
                
            logger.log(f"Pinecone Available indexes List df :: \t {df}", "0")    
            pinecone.init(api_key=self.pineCone_apiKey, environment='us-west4-gcp')
            openai.api_key = self.openAI_apiKey                 

            logger.log(f"Pinecone Available indexes List  :: \t {pinecone.list_indexes()}", "0")    
            # Creating index
            if self.index_name not in pinecone.list_indexes():
                logger.log(f" \n'{self.index_name}' index not present. Creating New!!!\n", "0")
                pinecone.create_index(name = self.index_name, dimension=self.dimensions, metric='cosine')
                self.my_index = pinecone.Index(index_name=self.index_name)
            else:
                logger.log(f" \n'{self.index_name}' index is present. Loading now!!!\n", "0")
                self.my_index = pinecone.Index(index_name=self.index_name)
            logger.log(f"Pinecone Available indexes List  :: \t {pinecone.list_indexes()}", "0")    

            df.columns = ['_'.join(column.lower().split(' ')) for column in df.columns]
            df.fillna("N/A",inplace=True)
            
            if self.modelScope == "G" :
                self.enterpriseName = ""
            
            self.enterpriseEntityInfo = (self.enterpriseName + "_" +self.entity_type).upper()
            logger.log(f"enterpriseEntityInfo  ::: \t {self.enterpriseEntityInfo}", "0")    
            df['enterprise'] = self.enterpriseEntityInfo
            
            required_colNameList = ['id','description']
            logger.log(f"\nBefore df Column Name  change::  {df.columns.tolist()},\n {df.columns}", "0")    
            df.columns = required_colNameList + df.columns[len(required_colNameList):].tolist()
            logger.log(f"\n After df Column Name change:: {df.head()},\n {df.head()}", "0")    
            df['embedding'] = get_embeddings(df['description'].to_list(), engine=self.engineName)   
            metadata = df.loc[:, ~df.columns.isin(['id','embedding'])].to_dict(orient='records')  # remove not required columns 

            upsert = list(zip(df['id'], df['embedding'], metadata))
            _ = self.my_index.upsert(vectors=upsert)
            logger.log(f"{self.my_index.describe_index_stats()}","0")

            logger.log(f"\nOpenAI_PineConeVector class trainData:::\t{self.my_index}","0")
            result = f" '{self.index_name}' Index Creation SUCCESSFUL for filter: '{self.enterpriseEntityInfo}'. "
            logger.log(f"\nOpenAI_PineConeVector class trainData Result:::{result}\n","0")
            return result
            
        except Exception as e:
            logger.log(f" '{self.index_name}' Index Creation FAILED for filter: '{self.enterpriseEntityInfo}'. ","0")
            logger.log(f"OpenAI_PineConeVector class trainData() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n OpenAI_PineConeVector class trainData() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def getLookupData(self):               
        try:
            
            logger.log("inside PineConeVector class LookUpData()","0")
            id_list                 = []
            finalResult             = ""
            queryJson               = "" 
            finalResultJson         = {}
            
            pineCone_json =  request.get_data('jsonData', None)
            pineCone_json = json.loads(pineCone_json[9:])
            logger.log(f"\nPineConeVector class getLookupData() pineCone_json:::\t{pineCone_json} \t{type(pineCone_json)}","0")

            if "openAI_apiKey" in pineCone_json and pineCone_json["openAI_apiKey"] != None:
                self.openAI_apiKey = pineCone_json["openAI_apiKey"]          
                logger.log(f"\nPineConeVector class LookUpData() openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
                openai.api_key = self.openAI_apiKey                 

            if "pineCone_apiKey" in pineCone_json and pineCone_json["pineCone_apiKey"] != None:
                self.pineCone_apiKey = pineCone_json["pineCone_apiKey"]           
                logger.log(f"\nPineConeVector class LookUpData() pineCone_apiKey:::\t{self.pineCone_apiKey} \t{type(self.pineCone_apiKey)}","0")

            if "index_name" in pineCone_json and pineCone_json["index_name"] != None:
                self.index_name = pineCone_json["index_name"]
                logger.log(f"\nPineConeVector class LookUpData() index_name:::\t{self.index_name} \t{type(self.index_name)}","0")
            
            if "queryJson" in pineCone_json and pineCone_json["queryJson"] != None:
                queryJson = pineCone_json["queryJson"]
                logger.log(f"\nPineConeVector class LookUpData() queryJson:::\t{queryJson} has length ::: '{len(queryJson)}'\t{type(queryJson)}","0")
            
            if "enterprise" in pineCone_json and pineCone_json["enterprise"] != None:
                self.enterpriseName = pineCone_json["enterprise"]
                logger.log(f"\nPineConeVector class LookUpData() enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            if "modelScope" in pineCone_json and pineCone_json["modelScope"] != None:
                self.modelScope = pineCone_json["modelScope"]
                logger.log(f"\nPineConeVector class LookUpData() modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")
            
            if "entity_type" in pineCone_json and pineCone_json["entity_type"] != None:
                self.entity_type = pineCone_json["entity_type"]
                logger.log(f"\nentity_type:::\t{self.entity_type} \t{type(self.entity_type)}","0")
            
            if self.modelScope == "G":
                self.enterpriseName = ""

            openai.api_key  =  self.openAI_apiKey         
            pinecone.init(api_key=self.pineCone_apiKey, environment='us-west4-gcp')
            self.enterpriseEntityInfo = (self.enterpriseName + "_" +self.entity_type).upper()
            logger.log(f"\nenterpriseEntityInfo:::\t{self.enterpriseEntityInfo} \t{type(self.enterpriseEntityInfo)}","0")
            
            pinecone_IndexList = pinecone.list_indexes()
            if self.index_name in pinecone_IndexList:
                self.my_index = pinecone.Index(index_name=self.index_name)
                if self.my_index != "":
                    logger.log(f"\n\n'{self.index_name}' index loaded successfully for filter: '{self.enterpriseEntityInfo}\n'")
            else:
                logger.log(f"OpenAI_PineConeVector class getLookUP()::: \nIndex_Name: {self.index_name} not found in pinecone_IndexList: {pinecone_IndexList}","0")
                message = f"Index_Name: '{self.index_name}' not found in pinecone_IndexList. Available IndexList: {pinecone_IndexList}"
                errorXml = common.getErrorXml(message, "")
                raise Exception(errorXml)
            
            if self.index_name == "document":
                for key in queryJson:
                    # because in document case I get directly list and not json
                    response = self.my_index.query(vector=get_embedding(key, engine=self.engineName),filter={"enterprise": self.enterpriseEntityInfo},top_k=10, include_metadata=True)
                    if response["matches"][0]["score"] >= 0.75 and key in j['metadata']['description']:
                        id_list.append(response["matches"][0]["id"])
                
                logger.log(f"\n\n id_list:::{id_list} has length :::'{len(id_list)}' \t {type(id_list)}\n")
                finalResult = str(id_list)
                
            elif self.index_name == "item" or self.index_name == "vision-masters":
                for key in queryJson:
                    if len(queryJson[key]) > 0:
                        if self.index_name == "item":
                            response = self.my_index.query(vector=get_embedding(queryJson[key], engine=self.engineName),filter={"enterprise": self.enterpriseEntityInfo},top_k=1, include_metadata=True)
                            logger.log(f"response:::: {response}")
                            finalResultJson[key] = {"material_description": response["matches"][0]["metadata"]["material_description"], 
                                                    "id": response["matches"][0]["id"]}  if len(response["matches"]) > 0 else response
                        
                        elif self.index_name == "vision-masters":
                            response = self.my_index.query(vector=get_embedding(queryJson[key], engine=self.engineName),filter={"enterprise": self.enterpriseEntityInfo},top_k=1, include_metadata=True)
                            logger.log(f"response:::: {response}")
                            finalResultJson[key] = {"material_description": response["matches"][0]["metadata"]["description"], 
                                                    "id": response["matches"][0]["id"],
                                                    "score" : response["matches"][0]["score"]}  if len(response["matches"]) > 0 else response
                    else:
                        logger.log(f"Empty description found for line number:::'{key}'")
                
                logger.log(f"\n\nfinalResultJson:::{finalResultJson} has length ::: '{len(finalResultJson)}' \t {type(finalResultJson)}\n")
                finalResult = str(finalResultJson)

            else:
                logger.log(f"OpenAI_PineConeVector class getLookUP()::: \nIndex_Name: {self.index_name} not found in pinecone_IndexList: {pinecone_IndexList}","0")
                message = f"Index_Name: '{self.index_name}' not found in pinecone_IndexList. Available IndexList: {pinecone_IndexList}"
                errorXml = common.getErrorXml(message, "")
                raise Exception(errorXml)
            
            return finalResult
        
        except Exception as e:
            logger.log(f"OpenAI_PineConeVector class getLookUP() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n OpenAI_PineConeVector class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

