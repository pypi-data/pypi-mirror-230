import requests
embeddingsCategory='Embedding models'
embeddingsModel = 'Ada v2'
usageFieldName = "Usage"
inputFieldName = "Input"
outputFieldName = "Output"
thousand_constant = 1000
def calculate_openai_pricing(category, model,total_embedding_token_count,prompt_llm_token_count,completion_llm_token_count):
    rawData = requests.get('https://openai-api-pricing-web-api.onrender.com/openai')
    pricingJson = rawData.json()
    return calculate_costs(pricingJson, category, model, total_embedding_token_count,prompt_llm_token_count,completion_llm_token_count)
    
def get_embeddings_data(pricingJson):
    return filter_pricing_data_by_model(pricingJson, embeddingsCategory,embeddingsModel)
    
def filter_pricing_data_by_model(pricingData, category, model):
    filteredData = {}
    for pricingCategory in pricingData:
        if pricingCategory == category:
            for item in pricingData[category]:
                if "Model" in item and item["Model"] == model:
                    filteredData[category] = [item]
    return filteredData 

def calculate_costs(pricingJson,category, model, total_embedding_token_count,prompt_llm_token_count,completion_llm_token_count):
    enginePricingData = filter_pricing_data_by_model(pricingJson, category, model)
    embeddingsModelPricing = get_embeddings_data(pricingJson)
    costForThousandCurrency,embeddingsCost = calculate_embeddings_token_price(embeddingsModelPricing,total_embedding_token_count)
    costForThousandCurrency,promptCost = calculate_prompt_token_price(enginePricingData,category,prompt_llm_token_count)
    costForThousandCurrency,completionTokenCost = calculate_completion_token_price(enginePricingData,category,completion_llm_token_count)
    return costForThousandCurrency,embeddingsCost,promptCost,completionTokenCost,(embeddingsCost + promptCost + completionTokenCost)

def getPricingInfo(priceText):
    currency = priceText[0]
    number = float(priceText[1:])
    return currency, number

def calculate_embeddings_token_price(embeddingsModelPricing,total_embedding_token_count):
    costForThousandCurrency,costForThousandNumber = getPricingInfo(embeddingsModelPricing[embeddingsCategory][0][usageFieldName])
    calculated_cost = (total_embedding_token_count/1000) * costForThousandNumber
    calculated_cost_rounded = round(calculated_cost,3)
    return costForThousandCurrency,calculated_cost_rounded
def calculate_prompt_token_price(enginePricingData,category, total_prompt_token_count):
    costForThousandCurrency,costForThousandNumber = getPricingInfo(enginePricingData[category][0][inputFieldName])
    calculated_cost = (total_prompt_token_count/1000) * costForThousandNumber
    calculated_cost_rounded = round(calculated_cost,3)
    return costForThousandCurrency,calculated_cost_rounded
def calculate_completion_token_price(enginePricingData,category, total_completion_token_count):
    costForThousandCurrency,costForThousandNumber = getPricingInfo(enginePricingData[category][0][outputFieldName])
    # round the cost to 3rd decimal place
    calculated_cost = (total_completion_token_count/1000) * costForThousandNumber
    calculated_cost_rounded = round(calculated_cost,3)
    return costForThousandCurrency,calculated_cost_rounded

# calculate_openai_pricing("GPT-3.5 Turbo","4K context",{
#     'total_embedding_token_count': 21111,
#     'prompt_llm_token_count': 10031,
#     'completion_llm_token_count': 123123
# })

#  print('Embedding Tokens: ', token_counter.total_embedding_token_count, '\n',
#       'LLM Prompt Tokens: ', token_counter.prompt_llm_token_count, '\n',
#       'LLM Completion Tokens: ', token_counter.completion_llm_token_count, '\n',
#       'Total LLM Token Count: ', token_counter.total_llm_token_count)