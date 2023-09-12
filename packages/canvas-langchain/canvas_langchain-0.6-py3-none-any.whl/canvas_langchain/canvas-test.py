from canvas import CanvasLoader

loader = CanvasLoader(
	api_url = "https://umich.instructure.com",
	api_key = "1770~Q5PJ54el1HFIqnAXT05ZE50gykHSGMfViMDsMxZTO1nSBoKiCLkoMyd7Vlm0iZZh",
	course_id = (17700000000000000 + 42564)) # 574538
documents = loader.load()

# 1770~Q5PJ54el1HFIqnAXT05ZE50gykHSGMfViMDsMxZTO1nSBoKiCLkoMyd7Vlm0iZZh john@ururk.com
# 1770~3maF9G8sFI8JhFTQzvHGU2g7l1Y7sB4rVnqmmBmKwrzHtoxbcBd5ea6dJY5QQwLN jparisea@umich.edu


print("\nDocuments:\n")
print(documents)

print("\nInvalid files:\n")
print(loader.invalid_files)
print("")

print("\nErrors:\n")
print(loader.errors)
print("")