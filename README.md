# Demo Python application

## Application links

- [Sample RUM app](http://ANY_K8S_NODE:30080/lab) - Simple app for RUM testing
- [RabbitMQ](http://ANY_K8S_NODE:32080/) - guest/guest
- [Adminer](http://ANY_K8S_NODE:31080/) - SQL Client for MySQL

## Browser Synthetics

In order to get full end-to-end monitoring with Browser Synthetics, including traces, remember to propertly set [APM integration for Browser Tests](https://app.datadoghq.com/synthetics/settings/default).

## e2e Traces

RUM adds trace headers only to origins listed in [allowedTracingOrigins](https://docs.datadoghq.com/real_user_monitoring/connect_rum_and_traces/?tab=browserrum#rum-set-up). If you are not getting the headers, check if the origin is correct. It should include protocol, domain, and port.

<img src="img/RUM-headers.jpg" width="400px"/>

Context is propagated in message brokers, like RabbitMQ and Kafka, by message headers.

<img src="img/RabbitMQ-headers.jpg" width="400px"/>

## Notes

MySQL deployment has annotations for [AutoDiscovery](https://docs.datadoghq.com/agent/kubernetes/integrations/?tab=kubernetes).

The [app-python.yaml](kubernetes/app-python.yaml) has a few particularities with an intention behind.

It deploys two deployments of the same image, `app-python-v1` and `app-python-v2`. They have different metadata for version.  Both are backends to the service `app-python`.  It creates a simple load balancing between two versions to demostrate tracking of multiple deployments.

Another difference is how `app-python-v1` and `app-python-v2` set universal tags and agent host.  The first, `v1`, uses the traditional methos of environment variables.  The second, `v2`, relies on the new [admisson controller](https://docs.datadoghq.com/agent/cluster_agent/admission_controller/).
