from enum import Enum

class URL(Enum):
    
    AUTH_LOGIN = "https://api.moorse.io/oauth/login"

    WEBHOOK = "https://api.moorse.io/v1/webhooks"
    SEARCH_WEBHOOK = "https://api.moorse.io/v1/webhooks/{}"

    TEMPLATE = "https://api.moorse.io/v1/templates"
    SEARCH_TEMPLATE = "https://api.moorse.io/v1/templates/{}"

    REPORT = "https://api.moorse.io/v1/reports/total-messages?beginDate={}&endDate={}"
    REPORT_BY_CHANNEL = "https://api.moorse.io/v1/reports/total-messages-channels?beginDate={}&endDate={}"
    REPORT_BY_TIMELINE = "https://api.moorse.io/v1/reports/total-messages-timeline?beginDate={}&endDate={}"

    BILLING = "https://api.moorse.io/v2/whatsapp/{}/credit"

    WHATSAPP_TEXT_MESSAGE = "https://api.moorse.io/v2/whatsapp/{}/send-message"
    WHATSAPP_FILE_MESSAGE = "https://api.moorse.io/v2/whatsapp/{}/send-file"
    WHATSAPP_LIST_MENU_MESSAGE = "https://api.moorse.io/v2/whatsapp/{}/send-list-menu"
    WHATSAPP_BUTTONS_MESSAGE = "https://api.moorse.io/v2/whatsapp/{}/send-buttons"
    WHATSAPP_TEMPLATE_MESSAGE = "https://api.moorse.io/v2/whatsapp/{}/send-template"

    SMS_TEXT_MESSAGE = "https://api.moorse.io/v1/sms/{}/send-message"

    INSTAGRAM_TEXT_MESSAGE = "https://api.moorse.io/v1/instagram/{}/send-message"

    INTEGRATION = "https://api.moorse.io/v2/whatsapp"
    SEARCH_INTEGRATION = "https://api.moorse.io/v2/whatsapp/{}"
    SEARCH_INTEGRATION_STATUS = "https://api.moorse.io/v2/whatsapp/{}/status"