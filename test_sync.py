from dotenv import load_dotenv 
load_dotenv() 
from state_store import init_db 
init_db() 
from sync import run_sync 
run_sync()