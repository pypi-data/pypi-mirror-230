# amzn-micro-coral

A minimalistic implementation of a Coral client, used mainly for
people who are working in contexts where they may not be able to
import Coral clients directly.

## Usage

Service calls are entirely unopinionated, so you better be good at
reading Coral client configs. A regular instantiation of the service
would be:

    from amzn_micro_coral import CoralService, CoralAuth

    my_service = CoralService(
        url="https://my-service.amazon.com",
        auth=CoralAuth.midway(sentry=False),
    )

    r = my_service.post("MyService.MyOperation", data={"param1": "value1"})
    result = r.json()

The client does do a basic level of error checking in case the Coral
service returns the standard error message in the form `{"__type":
"<message>"}`.

## Samples

This module also provides some very basic classes for interacting with
generic services:

    from amzn_micro_coral import crux

    r = crux.post(<...>)

Some may provide more features than others but have no guarantee of
always working into the future.
