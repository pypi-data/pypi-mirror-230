class AnomalyDetectionClass:

    def __init__(self, MailClassObject, PermitImprintObject):
        self.mail_class = MailClassObject
        self.permit_imprint = PermitImprintObject

        # Initialize anomaly to false
        self.is_anomaly = False
        self.anomaly_types = []
        self.anomaly_confs = {}

        self.check_for_anomaly()
        self.create_anomaly_conf()

    def get_anomaly_type(self):
        # Webapat wants this as a string not a list
        # so we will add , in between anomaly types and combine
        # into one string
        anomaly_type_str = ""
        for anomaly_type in self.anomaly_types:
            anomaly_type_str += anomaly_type + ","

        return anomaly_type_str

    def get_anomaly_types_dict(self):
        # Webapat wants a list of anomaly conf by anomaly type along with supplemental information example:
        # "anomaly_types": [{"confidence": 51.4, "anomaly_type": "anomaly_01", "supplemental_information": "SI
        # 3"}]
        anomaly_type = []
        for ft, conf in self.anomaly_confs.items():
            anomaly_type.append({"confidence": conf, "anomaly_type": ft})
        return anomaly_type

    def anomaly_found(self):
        return self.is_anomaly

    def create_anomaly_conf(self):
        if self.is_anomaly:
            for anomaly_id in self.anomaly_types:

                if anomaly_id in self.mail_class.anomaly_type:
                    metrics = self.mail_class.describe_anomaly_metrics()
                    self.anomaly_confs[anomaly_id] = metrics[f"anomaly_{anomaly_id}"]['anomaly_confidence']
                if anomaly_id in self.permit_imprint.anomaly_type:
                    metrics = self.permit_imprint.describe_anomaly_metrics()
                    self.anomaly_confs[anomaly_id] = metrics[f"anomaly_{anomaly_id}"]['anomaly_confidence']

    def check_for_anomaly(self):
        if self.mail_class.is_anomaly:
            self.is_anomaly = True
            self.anomaly_types.extend(anomaly_type for anomaly_type in self.mail_class.anomaly_type)
        if self.permit_imprint.is_anomaly:
            self.is_anomaly = True
            self.anomaly_types.extend(anomaly_type for anomaly_type in self.permit_imprint.anomaly_type)
