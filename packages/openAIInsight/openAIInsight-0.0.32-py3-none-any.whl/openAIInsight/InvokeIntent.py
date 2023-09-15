import requests, json, traceback, openai
from flask import request
import loggerutility as logger
import commonutility as common
import os

class InvokeIntent:
    def getInvokeIntent(self):
        try:
            logger.log(f"\n\nInside getInvokeIntent()","0")
            jsonData = request.get_data('jsonData', None)
            intentJson = json.loads(jsonData[9:])
            logger.log(f"\njsonData openAI class::: {jsonData}","0")
            
            finalResult     =  {}
            openAI_APIKey   =  intentJson['openAI_APIKey'] 
            intent_input    =  intentJson['intent_input']
            enterprise      =  intentJson['enterprise']     
            fileName        = "intent_Instructions.txt"
            openai.api_key  = openAI_APIKey
            
            logger.log(f"\n\njsonData getIntentService fileName::: \t{fileName}\n","0")
            
            if os.path.exists(fileName):
                intent_trainingData = open(fileName,"r").read()
            else:
                logger.log(f"\n\n{fileName}  does not exist.\n","0")  
                message = f"The Intent API service could not be requested due to missing '{fileName}' file. "
                return message
                
            logger.log(f"\n\ngetIntentService before conversion :::::: {type(intent_trainingData)} \n{intent_trainingData}\n","0")
            replaced_trainingData = intent_trainingData.replace("<intent_input>", intent_input)
            logger.log(f"\n\ngetIntentService after replacing <intent_input> :::::: \n{replaced_trainingData} \n{type(replaced_trainingData)}","0")
            messageList = json.loads(replaced_trainingData)
            logger.log(f"\n\nmessageList after conversion :::::: {messageList} \n{type(messageList)}","0")
            
            logger.log(f"\n\nfinal messageList :::::: {messageList}","0")

            response = openai.ChatCompletion.create(
                                                    model="gpt-3.5-turbo",
                                                    messages=messageList,
                                                    temperature=0,
                                                    max_tokens=1800,
                                                    top_p=1,
                                                    frequency_penalty=0,
                                                    presence_penalty=0,
                                                )
            logger.log(f"\n\nResponse openAI endpoint::::: {response} \n{type(response)}","0")
            finalResult=str(response["choices"][0]["message"]["content"])
            logger.log(f"\n\nOpenAI endpoint finalResult ::::: {finalResult} \n{type(finalResult)}","0")
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getIntentService exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
        

