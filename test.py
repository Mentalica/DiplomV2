import inspect
import os

def get_classes_and_attributes(file_path):
    classes = []
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            code = compile(file.read(), file_path, 'exec')
            # Остальной код для извлечения классов и атрибутов
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {str(e)}")

        for obj in code.co_consts:
            if inspect.isclass(obj):
                class_name = obj.__name__
                class_attributes = [name for name, _ in inspect.getmembers(obj) if not name.startswith('__')]
                classes.append((class_name, class_attributes))
    return classes

def get_all_classes_and_attributes(folder_path):
    all_classes = []
    for root, dirs, files in os.walk(folder_path):
        print(dirs)
        for file in files:
            # print(file)
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                classes = get_classes_and_attributes(file_path)
                all_classes.extend(classes)
    return all_classes

# Укажите путь к папке проекта
current_directory = os.getcwd()
print(current_directory)
project_folder = ''  # Установите путь к папке проекта
all_classes = get_all_classes_and_attributes(project_folder)

# Вывод всех классов, их полей и методов
for class_name, attributes in all_classes:
    print(f"Class: {class_name}")
    print(f"Attributes: {attributes}")
    print()
