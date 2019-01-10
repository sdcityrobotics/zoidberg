Navigation
==========

Navigation underwater is particularly challenging for a number of reasons, and
has been a topic of active research for a long time. It will probably remain so
for some time to come, despite a few `DARPA challenges <https://www.wired.com/2016/05/darpa-wants-underwater-gps-system-seafaring-robots/>`_
designed to adress the issue with ocean scale underwater positioning system
using acoustics.

While it is hard to imagine a world without GPS at this point, in the
1980s access to the network was restricted, and it was only in 2000 that
full accuracy of the positioning network was allowed for use by the civilians.
There are still a few stipulations on use required in all GPS enabled devices
to prevent its use in ballistic missle systems, and a standing contigency to
revoke its use in wartime. GPS requires the reception of satilite broadcasts,
and so it is not possible to use this system underwater beneath a foot or so of
depth. Interestingly enough, there is a siginifcant interest in GPS free
navigation in the military since the sucesful `Iranian spoofing attack <https://en.wikipedia.org/wiki/Iran%E2%80%93U.S._RQ-170_incident>`_
on a US drone.

Without the option of GPS, it is important to use other navigation techniques.
A time tested method is `dead-reckoning <https://en.wikipedia.org/wiki/Dead_reckoning>`_
, which has been used by sailors
once they discoved an accurate compass. Dead-reckoning requries the measurement
of the ships speed, which can be done by dropping a log off the bow and waiting
for it to pass the stern. With a heading, it is possible to anticipate where
the ship will be on a map without landmarks or celestial indicators, which can
be very important in the open ocean with overcast skys. These basic instruments
(compass and speed measurement) have been improved greatly since early
navigation days, with corrisponding increases of position accuracy.

The robot has another valuble source of navigation from the acoustic pinger
deployed as a part of the competition. The regular timing and fixed location of
the signal source could make it positioning tool. There are a number of
established challenges to this form of navigation, including acoustic multipath
and the angular resolution of the receiving array. These challenges mean that
the acoustics will likely only be used to get additionally points in the
competition, and not for navigation until there is significant further
development.

Focusing on dead-reckoning navigation, two measurements are requred for
accurate positioning; heading and velocity. Both of these measurements are
avalible to the robot in two flavors, relative and absolute. Relative quantities
are found by integrating an inertial measurement, angular velocity and
acceleration, respectivly. Inertial measurement have relativly good precision,
but thier error increases with integration time. An important consideration
when using these measurements is the amount of time over which the integration
can be considerd accurate, after which time it should be restarted.

Given that inertial measurements are only valid for a length of time, it is
best to use abosule measurements. These are taken directly, in our case using a
compass and a doppler velocity log (DVL). There are challenges with both of
these measurements which require the mention of the relative measuements in
the first place. As these effects are further studied and adressed, perhaps it
will not be necassary to use relative measurements further. This would
significantly clarify the navigation of Zoidberg.

The compass is influenced heavily by the internal magnetic field of Zoidberg,
including perminant effects of iron and transient fields caused by large
currents in motor power cables. Additionally, the external magnetic field
inside the competition pool is corrupted by the large amount of iron used in
its construction. This effect is expected to be strongest near the walls and
basment of the tank. The current stratagy for absolute heading measurement will
be to minimize internal interference with the compass, and work to identify
places in the tank when the heading measurement is trusted.

The DVL is a relativly untested system on Zoidberg because it does not seem to
work well in small pools. This is marked by a great deal of dropped
measurements, whcih then require a back-up velocity measurement system. It is
posible that it will just work in the competition pool, but until this is
established it is necassary operate as if it will not, to be safe. The most
simple way to do this is to measure the relationship between motor input and
robot speed. If this is well behaved (more power gives more speed, mostly
linearly) then it will be possible to predict robot speed from motor input. It
would be nice to additionally calculate speed from acceleration, but the accuracy
of this measurement has to be established.
