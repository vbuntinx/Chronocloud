from urllib.request import urlopen

os.makedirs('legislation',exist_ok=True)
for year in range(1900,2016):
    response=urlopen('http://www.matthewlippoldwilliams.com/documents/data-sets/'+str(year)+'/'+str(year)+'.txt')
    page_source=response.read().decode('utf-8')
    with open('legislation/'+str(year)+'.txt','w',encoding='utf-8') as file:
        file.write(page_source)
    print(year)
