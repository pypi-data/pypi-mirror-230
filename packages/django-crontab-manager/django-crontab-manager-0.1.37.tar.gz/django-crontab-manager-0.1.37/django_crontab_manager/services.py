from .models import Schedule
from .models import Result


def update_schedules_code(items):
    changed_items = []
    for item in items:
        old_code = item.code
        new_code = item.get_code()
        if old_code != new_code:
            item.code = new_code
        changed_items.append(item)
    if changed_items:
        Schedule.objects.bulk_update(changed_items, fields=["code"])
    return changed_items

def update_results_success_determination(items):
    changed_items = []
    for item in items:
        old_success_value = item.success
        new_success_value = item.success_determination()
        if old_success_value != new_success_value:
            changed_items.append(item)
    if changed_items:
        Result.objects.bulk_update(changed_items, fields=["success"])
    return changed_items
