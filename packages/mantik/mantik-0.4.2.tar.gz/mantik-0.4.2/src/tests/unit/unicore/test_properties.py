import mantik.unicore.properties as _properties


class TestProperties:
    def test_from_dict(self, example_job_property_response):
        properties = _properties.Properties.from_dict(
            example_job_property_response
        )
        assert properties.status == _properties.Status.SUCCESSFUL
        assert properties.logs == [
            "Tue Oct 05 11:39:44 CEST 2021: "
            "Created with ID f0e40654-c5f9-4684-b8b1-c65ef4000125",
            "Tue Oct 05 11:39:44 CEST 2021: Created with type 'JSON'",
            "Tue Oct 05 11:39:44 CEST 2021: Client: Name: "
            "UID=test-user@emai.domain\nXlogin: uid: [test-user], "
            "gids: [test-project, addingOSgroups: true]\nRole: user: "
            "role from attribute source\nQueues: ["
            "gpus:batch:develgpus:devel:"
            "develbooster, selected=gpus]\nSecurity tokens: User: "
            "UID=test-user@email.domain\nClient's original IP: 90.189.81.115",
            "Tue Oct 05 11:39:46 CEST 2021: No staging in needed.",
            "Tue Oct 05 11:39:46 CEST 2021: Status set to READY.",
            "Tue Oct 05 11:39:46 CEST 2021: Status set to PENDING.",
            "Tue Oct 05 11:39:46 CEST 2021: No application to execute, "
            "changing action status to POSTPROCESSING",
            "Tue Oct 05 11:39:46 CEST 2021: Status set to DONE.",
            "Tue Oct 05 11:39:46 CEST 2021: Result: Success.",
            "Tue Oct 05 11:39:46 CEST 2021: Total: 0 sec., "
            "Stage-in: 0 sec., Stage-out: 0 sec.",
        ]
