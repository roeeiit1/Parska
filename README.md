# Parska
Parses alert manager alerts and inserts them into kafka topic
# Environment Variable configuration
parska_port - Port on which parska will be listening on ```defaults to 5000```

kafka_topic - Topic to which parska will write to ```defaults to alerts_topic```
# Endpoints
```
http://parska-dns:configured-port/
```
# Output alert model
```
{
    <json_with_alert_data (no inner json)>,
    "groupKey": <string>, 
    "receiver": <string>,
    "groupLabels": <object>,
    "commonLabels": <object>,
    "commonAnnotations": <object>,
    "externalURL": <string>
}
```
# Expected model
```
{
  "version": "4", // is removed from final alert by default
  "groupKey": <string>, 
  "status": "<resolved|firing>", // (removed by default) status of alertmanage, uneeded in by alert basis
  "receiver": <string>,
  "groupLabels": <object>,
  "commonLabels": <object>,
  "commonAnnotations": <object>,
  "externalURL": <string>,
  "alerts": [
    {
      "labels": <json>,
      "annotations": <json>,
    },
    {
      "labels": <json>,
      "annotations": <json>,
    },
    ... 
  ]
}
```