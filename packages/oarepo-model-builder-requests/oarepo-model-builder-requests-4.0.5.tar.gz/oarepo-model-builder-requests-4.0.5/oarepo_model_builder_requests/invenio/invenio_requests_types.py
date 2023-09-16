from pathlib import Path

from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder
from oarepo_model_builder.utils.python_name import module_to_path


class InvenioRequestsTypesBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_types"
    section = "requests"
    template = "requests-types"

    def finish(self, **extra_kwargs):
        super(InvenioBaseClassPythonBuilder, self).finish() # calls super().finish() of InvenioBaseClassPythonBuilder
        vars = self.vars

        for request_name, request in vars["requests"].items():
            if not request["type"]["generate"]:
                continue
            module = request["type"]["module"]
            python_path = Path(module_to_path(module) + ".py")

            self.process_template(
                python_path,
                self.template,
                current_module=module,
                vars=vars,
                request=request,
                request_name=request_name,
                **extra_kwargs,
            )
