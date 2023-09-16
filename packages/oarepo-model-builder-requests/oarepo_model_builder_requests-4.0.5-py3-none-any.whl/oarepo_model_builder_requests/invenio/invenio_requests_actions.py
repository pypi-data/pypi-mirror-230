from pathlib import Path

from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder
from oarepo_model_builder.utils.python_name import module_to_path


class InvenioRequestsActionsBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_actions"
    section = "requests"
    template = "requests-actions"
    skip_if_not_generating = False

    def finish(self, **extra_kwargs):
        super(InvenioBaseClassPythonBuilder, self).finish() # calls super().finish() of InvenioBaseClassPythonBuilder
        if not self.generate:
            return
        vars = self.vars

        for request in vars["requests"].values():
            for action in request["actions"].values():
                if not action["generate"]:
                    continue
                module = action["module"]
                python_path = Path(module_to_path(module) + ".py")

                self.process_template(
                    python_path,
                    self.template,
                    current_module=module,
                    vars=vars,
                    action=action,
                    **extra_kwargs,
                )
