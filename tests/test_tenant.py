from tests.run_script import run_script

run_script("tenant --add test01 --app_id=12345 --app_secret=123456")
run_script("tenant --list_tenants")
run_script("tenant --add test02 --app_id=12345 --app_secret=123456")
run_script("tenant --list_tenants")
run_script("tenant --delete test01")
run_script("tenant --list_tenants")
run_script("tenant --delete test02")
run_script("tenant --list_tenants")
