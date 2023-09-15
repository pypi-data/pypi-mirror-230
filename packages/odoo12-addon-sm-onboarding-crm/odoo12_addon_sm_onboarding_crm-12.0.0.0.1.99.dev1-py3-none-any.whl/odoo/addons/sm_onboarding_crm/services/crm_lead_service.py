from odoo.addons.component.core import Component
from odoo.tools.translate import _

from . import schemas

CRM_TYPE_OPPORTUNITY = "opportunity"
UTM_SOURCE_BALENYA_XML_ID = "utm_source_onboarding_company_balenya_main_web_page"
ADDON_NAME = 'sm_onboarding_crm'


class CrmLeadDonationService(Component):
    _inherit = "crm.lead.service"
    _name = "crm.lead.service"
    _description = "Crm lead requests"

    def _source_is_onboarding(self, source_id):
        """
        Check if the source is from the onboarding process
        :return Bool :
        """
        utm_source = self.env['utm.source']
        if utm_source.search([int(source_id)]):
            return True
        return False

    def _validator_create(self):
        validator_schema = super()._validator_create().copy()
        validator_schema.update(schemas.SM_CRM_LEAD_CREATE)
        return validator_schema

    def _prepare_create(self, params):
        """
        Prepare data for crm lead creation
        :param dic params:
        :return:
        """
        create_dict = super()._prepare_create(params)
        # Todo create test in this case not source_xml_id in json
        if create_dict.get("source_xml_id", None) is None:
            res = super().create(**params)
            return res
        target_source_xml_id = params.get("source_xml_id")
        # TODO Create test return from a different source to UTM_SOURCE_BALENYA_XML_ID
        if target_source_xml_id == UTM_SOURCE_BALENYA_XML_ID:
            try:
                utm_source_record = self.env.ref(
                    ADDON_NAME + '.' + UTM_SOURCE_BALENYA_XML_ID)
            except Exception as e:
                raise ValueError(
                    _(f"The record data does not exist, addon: {ADDON_NAME}, id_record: {UTM_SOURCE_BALENYA_XML_ID} "
                      f"| error: {str(e)}"))
            create_dict.update(
                {"source_id": utm_source_record.id, "type": CRM_TYPE_OPPORTUNITY})

        return create_dict
