import vk_parser
import traceback

try:
	with open('settings.txt', 'r') as settings_file:
		params = settings_file.read().split('\n')
		user_id = params[0]
		exec('likes = ' + params[1])
		exec('subscribers = ' + params[2])
		key_word = params[3]
		stop_word = params[4]
		start_time = params[5]
		end_time = params[6]
		limit = int(params[7])
	vk_parser.parser(user_id=user_id, limit=limit, likes=likes, subscribers=subscribers, key_word=key_word, stop_word=stop_word, start_date=start_time, stop_date=end_time).parser_function()
except Exception:
	print(traceback.format_exc())
input()