import numpy as np


def valid_cubes(obsid):

    selall = np.arange(20)
    selno0 = np.arange(20)[1:]

    selall4 = np.arange(4)
    selall40 = np.arange(40)
    selno040 = np.arange(40)[1:]

    selno12 = [i for i in range(15)]
    selno12.pop(12)

    selno18 = [i for i in range(20)]
    selno18.pop(18)

    selno33 = [i for i in range(40)]
    selno33.pop(33)

    sel424 = [i for i in range(20)]
    sel424.pop(10)
    sel424.pop(5)

    sel441 = list(selno12)
    sel441.pop(5)

    sel472 = [i for i in range(40)]
    sel472.pop(33)
    sel472.pop(23)
    sel2293 = sel472
    sel472.pop(3)

    sel2125 = [i for i in range(20)]
    sel2125.pop(15)
    sel2125.pop(14)

    sel2128 = [i for i in range(20)]
    sel2128.pop(16)
    sel2128.pop(13)

    sel2131 = [i for i in range(10)]
    sel2131.pop(3)
    sel2131.pop(2)

    sel2292 = [i for i in range(20)]
    sel2292.pop(18)

    sel2423 = [i for i in range(72)]
    sel2423.pop(67)
    sel2423.pop(66)
    sel2423.pop(49)
    sel2423.pop(31)
    sel2423.pop(13)

    sel2442 =  [i for i in range(40)]
    sel2442.pop(33)

    sel2456 = [i for i in range(80)]
    sel2456.pop(73)
    sel2456.pop(72)
    sel2456.pop(53)
    sel2456.pop(33)
    sel2456.pop(13)

    hall = {406:selno0, 424:sel424, 427:selall, 430:np.arange(18),
             432:selno12, 437:selno12, 439:selno12, 441:sel441,
             467:selall, 468:selno0, 469:sel424, 472:sel472, 485:selno0, 486:selno0,
             497:selno0, 498:selno0, 553:selall, 560:selall, 562:selall40, 564:selall40,
            565:selall, 568:selall40, 569:selall, 597:selall, 600:selall, 606:selall,
            636:selall, 639:selall40, 641:selall, 642:selall40, 645:selall, 647:selall,
            649:selall, 652:selall, 654:selall, 656:selall, 657:selall[:-1], 658:selall[:-2],
            659:selall[:-2], 811:selall, 813:selall40, 841:selall, 842:selall40, 847:selall,
            899:selall, 900:selall,901:selall4, 2088:selall, 2090:selno33, 2099:selno18,
            2107:np.arange(5,20), 2109:selall, 2111:selall, 2113:selall, 2115:selall, 2117:selall,
            2119:selall, 2121:selall, 2123:selall, 2125:sel2125, 2128:sel2128, 2131:sel2131, 2292:sel2292,
            2293:sel2293, 2423:sel2423, 2441:selall, 2442:sel2442, 2454:selall, 2456:sel2456, 2464:selall, 2487:selall,
            2493:selall, 2494:selall, 2500:selall, 2501:selall, 2502:selall, 2503:selall, 2504:selall, 2505:selall,
            2506:selall, 2507:selall, 2508:selall, 2509:selall, 2510:selall, 2511:selall, 2512:selall, 2513:selall,
            2514:selall, 2515:selall, 2516:selall, 2517:selall, 2518:selall, 2519:selall, 2520:selno0}

    return hall[obsid]


