import os
import requests
import asyncio
import httpx
import pandas as pd

global_url = "https://pricing.us-east-1.amazonaws.com"

def make_request(url:str):
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        raise ConnectionError(url, res.status_code)

    
    
async def query_region(url:str, region:str) -> pd.DataFrame:
    print(url)
    async with httpx.AsyncClient(http2=True) as client:
        pricings = await client.get(url,  timeout=25.0)
    if pricings.status_code != 200:
        raise ConnectionError(url, pricings.status_code)
    
    pricings = [line.split(',') for line in pricings._content.decode('utf-8').splitlines()[5:]]
    df = pd.DataFrame(pricings[1:], columns=pricings[0])
    df.LeaseContractLength = df.LeaseContractLength.astype(str)
    df.LeaseContractLengthUnit = df.LeaseContractLengthUnit.map({'year' : 'yr', 'hour' : 'Hrs'})
    df.LeaseContractLength = df[['LeaseContractLength', 'LeaseContractLengthUnit']].agg(''.join, axis=1).astype("category")
    df['TermType'] = df.Location.apply(lambda x: (x == 'Any') * 'ComputeSavingsPlans' + (x != 'Any') * 'EC2SavingsPlans')
    # df.loc[df.Location == 'Any', 'Location'] = region
    df['Location'] = region
    df.rename(columns={'DiscountedSKU' : 'SKU', 'SKU' : 'WeirdSKU', 'DiscountedRate' : 'PricePerUnit', 'DiscountedOperation' : 'operation'}, inplace=True)
    df[['TermType', 'Unit', 'Currency', 'LeaseContractLength', 'PurchaseOption', 'Location', 'operation']] = df[['TermType', 'Unit', 'Currency', 'LeaseContractLength', 'PurchaseOption', 'Location', 'operation']].astype('category')
    
    # regex to check if this is indeed a shared instance, I had to use this as there is inconsistance in files per region
    # some include the region code in the beginning of the string
    selection = df.DiscountedUsageType.str.contains(r'(?<!\w)BoxUsage(?!\w)', regex=True)
    
    return df.loc[selection, ['SKU', 'WeirdSKU',  'TermType', 'Unit', 'PricePerUnit', 'Currency', 'LeaseContractLength', 'PurchaseOption', 'Location', 'Description', 'operation', 'DiscountedUsageType']]

async def collect_savings_plans(use_local_file=False) -> pd.DataFrame:
    if use_local_file:
        filepath = os.path.join('aws', "SP.csv")
        try:
            print('using local files')
            df =  pd.read_csv(filepath)
            df[['TermType', 'Unit', 'Currency', 'LeaseContractLength', 'PurchaseOption', 'Location', 'Operation']] = df[['TermType', 'Unit', 'Currency', 'LeaseContractLength', 'PurchaseOption', 'Location', 'Operation']].astype('category')
            return df
        except FileNotFoundError:
            print(f'no file found at {filepath}, default to using the API')
            return collect_savings_plans()
    latest_prices = make_request(global_url + "/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/index.json")
    url = latest_prices['versions'][0]['offerVersionUrl']
    prices_by_regions = make_request(global_url + url)
    prices_by_regions = {r['regionCode'] : r['versionUrl'] for r in prices_by_regions['regions']}

    used_by_TT = {'af-south-1',
                    'ap-east-1',
                    'ap-northeast-1',
                    'ap-northeast-2',
                    'ap-south-1',
                    'ap-southeast-1',
                    'ap-southeast-2',
                    'ca-central-1',
                    'eu-central-1',
                    'eu-north-1',
                    'eu-south-1',
                    'eu-west-1',
                    'eu-west-2',
                    'eu-west-3',
                    'me-south-1',
                    'sa-east-1',
                    'us-east-1',
                    'us-east-2',
                    'us-west-1',
                    'us-west-2'}
    
    works = [query_region(global_url + prices_by_regions[region].replace('.json', '.csv'), region) for region in used_by_TT]
    return pd.concat(await asyncio.gather(*works), ignore_index=True)

def collect_RI_OD() -> pd.DataFrame:
    print('loading file...')
    ec2data = pd.read_csv('https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.csv',
                          skiprows=5,
                          usecols = [0, 1, 3, 4, 8, 9, 10, 12, 13, 14, 15, 17, 19, 36, 38, 48, 49, 50, 74, 79, 81, 84],
                          dtype = {# use this to save significant ammount of memory and make your life easier
                          "TermType" : "category",
                          "Currency" : "category",
                          "PurchaseOption" : "category",
                          'CapacityStatus' : "category",
                          'OfferingClass' : "category",
                          'Location' : "category",
                          'Tenancy' : "category",
                          'Pre Installed S/W' : "category"
                          },
                          on_bad_lines='skip') # careful not to load everything, will probably burn down your computer
    print('Done !')
    # ec2data.to_csv("aws/raw_file.csv", index=False)
    # ec2data[['Normalization Size Factor']] = ec2data[['Normalization Size Factor']].astype('Int8') # crashes because of na (also some are 0.25)
    
    counts = ec2data.SKU.value_counts()
    s = set(counts.index[counts == 1])

    ec2data = ec2data.loc[~(ec2data.SKU.isin(s) & (ec2data.PricePerUnit == 0.)), :]

    
    upfronts = ec2data.loc[ec2data.Unit == 'Quantity', ['LeaseContractLength', 'PricePerUnit', 'SKU', 'OfferTermCode']]
    unit_mapping = {
        "Hrs" : 1,
        "hours" : 1,
        "Hours" : 1,
        "vCPU-Hours" : 1,
        "10 Hrs" : 10,
        "100 Hrs" : 100,
        "1yr" : 24 * 365 + 6, # hours in a year
        "3yr" : 26280
    }
    upfronts['hourly_price'] = upfronts.PricePerUnit / upfronts.LeaseContractLength.map(unit_mapping) # no /0 risks here
    upfronts['index'] = upfronts[['SKU', 'OfferTermCode']].agg('.'.join, axis=1)
    offer_to_prices = upfronts.set_index('index').to_dict()['hourly_price']
    new_prices = ec2data.loc[ec2data.Unit != 'Quantity', ['SKU', 'OfferTermCode']].agg('.'.join, axis=1).map(offer_to_prices)
    new_prices[new_prices.isna()] = 0
    ec2data.loc[ec2data.Unit != 'Quantity', 'PricePerUnit'] += new_prices * ec2data.loc[ec2data.Unit != 'Quantity', 'Unit'].map(unit_mapping)
    ec2data['PricePerUnit'] = ec2data['PricePerUnit']#.round(5) # this is the precision used by AWS
    return ec2data[ec2data.Unit != 'Quantity'].copy()

def collect_SP(use_local_file=False):
    if use_local_file:
        filepath = os.path.join('aws', "SP.csv")
        try:
            print('using local files')
            df =  pd.read_csv(filepath)
            df[['TermType', 'Unit', 'Currency', 'LeaseContractLength', 'PurchaseOption', 'Location', 'Operation']] = df[['TermType', 'Unit', 'Currency', 'LeaseContractLength', 'PurchaseOption', 'Location', 'Operation']].astype('category')
            return df
        except FileNotFoundError:
            print(f'no file found at {filepath}, default to using the API')
            return collect_SP()
    return asyncio.run(collect_savings_plans())

def collect(filepath=None)-> pd.DataFrame:
    # filepath = os.path.join('aws', "AWSPrices.csv")
    if filepath is not None:
        try:
            print('using local files')
            return pd.read_csv(filepath,
            dtype = {
                  "Unit" : "category",
                  "Currency" : "category",
                  "PurchaseOption" : "category",
                  'LeaseContractLength' : "category",
                  'Region Code' : "category",
                  'Tenancy' : "category",
                  'OfferingClass' : 'category',
                  'Operating System' : 'category',
                  'Pre Installed S/W' : "category"
                  }
                )
        except FileNotFoundError:
            print(f'no file found at {filepath}, default to using the API')
            return collect()
        
    RI_OD = collect_RI_OD()
    SP = collect_SP()

    # 
    # map the missing data of the SP file using the SKUs
    # 
    # '', '', 'UnusedBox', 'UnusedDed', 'HostUsage', 'Fargate', 'Request', 'Lambda'
    # tenancy_map = {'BoxUsage' : 'Shared', 'DedicatedUsage' : 'Dedicated', 'HostBoxUsage' : 'Host', }

    location_to_region_code = RI_OD.set_index('Location').to_dict()['Region Code']
    location_to_region_code['Any'] = 'Any'
    # applying the maps
    # SP['Instance Type'] = SP.SKU.map(SKU_to_instance_type)
    SP['Region Code'] = SP.Location
    # SP['Tenancy'] = SP.DiscountedUsageType.str.split(r"-|:", expand=True)[1].map(tenancy_map)
    SP.drop(columns='DiscountedUsageType', inplace=True)
    SP['OfferingClass'] = SP['TermType']
    SP.to_csv("aws/SP.csv", index = False)
    SP = SP.join(RI_OD[['SKU', 'Instance Type','Tenancy', 'Operating System', 'Normalization Size Factor', 'Pre Installed S/W']].drop_duplicates().set_index('SKU'), on='SKU')
    # careful, makes around 10 millions lines
    useful_cols = ['SKU', 'Instance Type','Normalization Size Factor','Operating System', 'Pre Installed S/W', 'operation', 'Tenancy', 'Region Code', 'TermType', 'LeaseContractLength', 'PurchaseOption', 'OfferingClass', 'Unit', 'Currency', 'PricePerUnit']
    final_prices = pd.concat(
        [RI_OD[useful_cols], SP[useful_cols]], ignore_index=True)
    # I should not do this : the Operating System columns describe the OS, which here is just Windaube
    # final_prices.loc[final_prices.operation == 'RunInstances:0800', 'Operating System'] = "Windows BYOL"
    final_prices.to_csv(filepath, index=False)
    return final_prices


if __name__ == "__main__":
    df = collect()
    print(df)


def aws() -> pd.DataFrame:
    """Query the AWS Bulk API to extract prices in a nice and tidy table. All prices given are per hour and amortized.

    CAREFUL : CAN TAKE UP TO 10 MINUTES TO RUN, DEPENDING ON YOUR INTERBNET CONNECTION

    Returns:
        pd.DataFrame: Tables with guid (SKU), region, operating system, pricing model and amortized price
    """
    df = collect(use_local_file=False)
    return df