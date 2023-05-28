from domain_models import DomainModels, DomainModel, DomainModelField, DomainEnum
from main_generator import MainGenerator

if __name__ == '__main__':

    # ORDER OF THE DOMAIN_MODELS IS IMPORTANT, FK DEPENDENCIES FIRST
    app_name = 'To Do'
    domain_models = DomainModels(app_name,
        [
            DomainModel("Task", [
                DomainModelField("title", "str", True, 255),
                DomainModelField("description", "str", True),
                DomainModelField("order", "int", True),
                DomainModelField("estimated_time_hours", "float", required=False),
                DomainModelField("due_date", "date", True),
                DomainModelField("status", "enum.Status", True, 100)
            ]),
            DomainModel("Comment", [
                DomainModelField("content", "str", True),
                DomainModelField("task", "Task", True)
            ]),
        ],
        [
            DomainEnum("Status", ["IN_PLANNING", "PLANNED", "CHECKING", "BLOCKED", "RESOLVED", "WONT_DO"])
        ]
    )

    try:
        generator = MainGenerator(domain_models)
        generator.generate()
    except Exception as e:
        print(e)
