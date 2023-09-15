class FraudDetectionClass:

    def __init__(self, IBIObject, MailClassObject, PermitImprintObject, IMPBObject):
        self.ibi = IBIObject
        self.mail_class = MailClassObject
        self.permit_imprint = PermitImprintObject
        self.impb = IMPBObject

        # Initialize Fraud to false
        self.is_fraud = False
        self.fraud_types = []
        self.fraud_confs = {}

        self.check_for_fraud()
        self.create_fraud_conf()

    def get_fraud_type(self):
        # Webapat wants this as a string not a list
        # so we will add , in between fraud types and combine
        # into one string
        fraud_type_str = ""
        for fraud_type in self.fraud_types:
            fraud_type_str += fraud_type + ","

        return fraud_type_str

    def get_fraud_types_dict(self):
        # Webapat wants a list of fraud conf by fraud type along with supplemental information example:
        # "fraud_types": [{"confidence": 51.4, "fraud_type": "TEST_FRAUD_TYPE_THREE", "supplemental_information": "SI
        # 3"}]
        fraud_type = []
        for ft, conf in self.fraud_confs.items():
            fraud_type.append({"confidence": conf, "fraud_type": ft})
        return fraud_type

    def fraud_found(self):
        return self.is_fraud

    def create_fraud_conf(self):
        if self.is_fraud:
            for ft in self.fraud_types:
                if ft in self.ibi.fraud_type:
                    metrics = self.ibi.describe_fraud_metrics()
                    if ft == "mismatch_humanReadableSN_decodedIBISN":
                        self.fraud_confs[ft] = metrics['serial_number_ibi']['fraud_confidence']
                    elif ft == "mismatch_humanReadableDate_decodedIBIDate":
                        self.fraud_confs[ft] = metrics['dates_ibi']['fraud_confidence']
                    elif ft == "invalid_IBI_SN":
                        self.fraud_confs[ft] = metrics['serial_number_construct_ibi']['fraud_confidence']
                if ft in self.mail_class.fraud_type:
                    metrics = self.mail_class.describe_fraud_metrics()
                    self.fraud_confs[ft] = metrics[ft]['fraud_confidence']

                if ft in self.permit_imprint.fraud_type:
                    metrics = self.permit_imprint.describe_fraud_metrics()
                    self.fraud_confs[ft] = metrics['fraud_confidence']
                if ft in self.impb.fraud_type:
                    metrics = self.impb.describe_fraud_metrics()
                    self.fraud_confs[ft] = metrics['impb_barcode']['fraud_confidence']

    def check_for_fraud(self):
        if self.ibi.is_fraud:
            self.is_fraud = True
            self.fraud_types.extend(fraud_type for fraud_type in self.ibi.fraud_type)
        if self.mail_class.is_fraud:
            self.is_fraud = True
            self.fraud_types.extend(fraud_type for fraud_type in self.mail_class.fraud_type)
        if self.permit_imprint.is_fraud:
            self.is_fraud = True
            self.fraud_types.extend(fraud_type for fraud_type in self.permit_imprint.fraud_type)
        if self.impb.is_fraud:
            self.is_fraud = True
            self.fraud_types.extend(fraud_type for fraud_type in self.impb.fraud_type)
