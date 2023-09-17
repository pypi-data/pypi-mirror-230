from sharetop.core.pig.pig_detail import get_pig_fcr

token = "f109298d079b5f60"


start_date = '2023-05-01'
end_date = '2023-05-16'

d = get_pig_fcr(token, start_date, end_date, is_explain=True)

print(d.to_dict("records"))