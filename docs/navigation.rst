Navigation
==========

#######################################
Global positioning system (GPS)
#######################################
Navigation underwater is particularly challenging compared to surface and air
based systems because there is no GPS. GPS requires the reception of satellite broadcasts,
and so it is not possible to use this system underwater beneath a foot or so of
water depth. This has been a topic of active research for a long time. It will probably remain so
for some time to come, despite a few `DARPA challenges <https://www.wired.com/2016/05/darpa-wants-underwater-gps-system-seafaring-robots/>`_
designed to address the issue with ocean scale underwater positioning system
using acoustics.

While it is hard to imagine a world without GPS at this point, in the
1980s access to the network was restricted, and it was only in 2000 that
full accuracy of the positioning network was allowed for use by the civilians.
There are still a few stipulations on use required in all GPS enabled devices
to prevent its use in ballistic missile systems, and a standing contingency to
revoke its use in wartime. This military history of the positioning system
provides some hint to the strategic importance of GPS, and wartime
contingencies continue to motivate GPS-free navigation for defense systems even
when the system is readily available.

#######################################
Dead Reckoning
#######################################
Without the option of GPS, it is important to use other navigation techniques.
A time tested method is `dead-reckoning <https://en.wikipedia.org/wiki/Dead_reckoning>`_
, used by sailors once they discovered an accurate compass.
Dead-reckoning requires the measurement of the ships speed, which can be
done by dropping a log off the bow and waiting for it to pass the stern.
With a heading, it is possible to anticipate where the ship will be on a
map without landmarks or celestial indicators, which can be very important
in the open ocean with overcast skies. These basic instruments (compass and
speed measurement) have been improved greatly since early
navigation days, with corresponding increases of position accuracy.


#######################################
Acoustic navigation
#######################################
The robot has another valuable source of navigation from the acoustic pinger
deployed as a part of the competition. The regular timing and fixed location of
the signal source could make it positioning tool. This is known as
`baseline navigation <https://en.wikipedia.org/wiki/Underwater_acoustic_positioning_system>`_.
There are a number of
established challenges to baseline navigation, including acoustic multi-path
and the angular resolution of the receiving array. These challenges mean that
the acoustics will likely only be used to get additionally points in the
competition, and not for navigation until there is significant further
development.

#######################################
Competition strategy
#######################################
Focusing on dead-reckoning navigation, two measurements are required for
accurate positioning; heading and velocity. Both of these measurements are
available to the robot in two flavors, relative and absolute. Relative quantities
are found by integrating an inertial measurement, angular velocity and
acceleration, respectively. Inertial measurement have relatively good precision,
but their error increases with integration time. An important consideration
when using these measurements is the amount of time over which the integration
can be considered accurate, after which time it should be restarted.

Given that inertial measurements are only valid for a length of time, it is
best to use absolute measurements. These are taken directly, in our case using a
compass and a Doppler velocity log (DVL). There are challenges with both of
these measurements which require the mention of the relative measurements in
the first place. As these effects are further studied and addressed, perhaps it
will not be necessary to use relative measurements further. This would
significantly clarify the navigation of Zoidberg.

The compass is influenced heavily by the internal magnetic field of Zoidberg,
including permanent effects of iron and transient fields caused by large
currents in motor power cables. Additionally, the external magnetic field
inside the competition pool is corrupted by the large amount of iron used in
its construction. This effect is expected to be strongest near the walls and
basement of the tank. The current strategy for absolute heading measurement will
be to minimize internal interference with the compass, and work to identify
places in the tank when the heading measurement is trusted.

The DVL is a relatively untested system on Zoidberg because it does not seem to
work well in small pools. This is marked by a great deal of dropped
measurements, which then require a back-up velocity measurement system. The
simplest way to do this is to measure the relationship between motor input and
robot speed. If this is well behaved (more power gives more speed, mostly
linearly) then it will be possible to predict robot speed from motor input.
