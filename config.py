LIMIT = 1000

FILTERS = {
	'likes': [False, '>', 15], # Вкл=True/выкл=False, >/>=/=/<=/<, число лайков
	'subscribers': [False, '=', 123094], # Вкл=True/выкл=False, >/>=/=/<=/<, число подписчиков
	'key_word': 'RAV', # Если строка пустая поиск по словам выключен
	'stop_word': [], # Если список пустой поиск по словам выключен, в список можно писать сколько хочешь слов
	'start_date': '', # Если строка пустая сортировка по дате выключена, формат: ГГГГ:МеМе:ДД: ЧЧ:МиМи:СС
	'stop_date': '' # Если строка пустая сортировка по дате выключена, формат: ГГГГ:МеМе:ДД: ЧЧ:МиМи:СС
}