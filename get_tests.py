#Python3
puls = 0
stop_list = ["exit","quit","выход", "стоп", 'stop']
print("Список доступного глобального пространства имён:", dir(), f"Для выхода используйте команды: {stop_list}")
send_one = "Всё что вы введете будет проанализировано и добавлено в контекст безопасного тестирования"
while True:
  puls += 1
  inp = input(f"{send_one}\n|{puls}>>")
  # АНАЛИЗ ВВОДА АРХИТЕКТОРА по тестированию
  if not inp:
    inp = "Архитектор промолчал, а это значит - молчание знак согласия!"
    print(inp)
  elif inp in stop_list:
    break
  else:
    print("Я прочитал, что Архитектор сказал:", inp)
  # ТЕСТ на основе результатов аналмза
  try:
    loc = {}
    result = eval(inp, None, loc)
    print("Ok\t\t\t\t"*5)
  except BaseException as be:
    result = f"ОШИБКА тестирования: {be}"  # +f", при EVAL({inp})! Рекомендуется: `__import__(`"
  send_one = str(result) + '\n' + str(loc)
