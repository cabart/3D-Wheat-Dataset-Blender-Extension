import bpy
from .leaf_colors import LEAF_COLORS, MaterialType, HEAD_COLORS

DEFAULT_COLORS = [
    [0, (0.0476, 0.3172, 0.0048, 1)],
    [0.1, (0.0635, 0.3714, 0.0099, 1)],
    [0.2, (0.0414, 0.3156, 0.0042, 1)],
    [0.3, (0.0231, 0.2456, 0.0003, 1)],
    [0.4, (0.0578, 0.3467, 0.0075, 1)],
    [0.5, (0.0364, 0.2844, 0.0025, 1)],
    [0.6, (0.0595, 0.3523, 0.0018, 1)],
    [0.7, (0.0292, 0.2774, 0.0002, 1)],
    [0.85, (0.0291, 0.2777, 0.0004, 1)],
    [1, (0.0345, 0.2974, 0.0008, 1)],
]

green_color = [
    [0.0, (0.07883632183074951, 0.11397947371006012, 0.02890823781490326, 1.0)],
    [
        0.05151515081524849,
        (0.07811016589403152, 0.11237052083015442, 0.031266000121831894, 1.0),
    ],
    [
        0.13333332538604736,
        (
            0.0765424519777298,
            0.10671187192201614,
            0.031155752018094063,
            0.9999999403953552,
        ),
    ],
    [
        0.1666666567325592,
        (0.08780986815690994, 0.12864409387111664, 0.043536681681871414, 1.0),
    ],
    [
        0.19696968793869019,
        (0.08089260756969452, 0.12319942563772202, 0.03994719684123993, 1.0),
    ],
    [
        0.20909090340137482,
        (
            0.10464318841695786,
            0.14454586803913116,
            0.055561281740665436,
            0.9999999403953552,
        ),
    ],
    [
        0.22727271914482117,
        (0.07621815800666809, 0.10815996676683426, 0.030215376988053322, 1.0),
    ],
    [
        0.2545454502105713,
        (0.07938601821660995, 0.11184240132570267, 0.025280136615037918, 1.0),
    ],
    [
        0.3121212124824524,
        (0.07759237289428711, 0.10937543213367462, 0.028562841936945915, 1.0),
    ],
    [
        0.3272727131843567,
        (
            0.09836322069168091,
            0.13727524876594543,
            0.04470231384038925,
            0.9999999403953552,
        ),
    ],
    [
        0.3393939137458801,
        (
            0.07265717536211014,
            0.10854347050189972,
            0.02956492081284523,
            0.9999999403953552,
        ),
    ],
    [
        0.4212121069431305,
        (0.06673413515090942, 0.09768269211053848, 0.03299335762858391, 1.0),
    ],
    [
        0.4424242377281189,
        (
            0.08093497157096863,
            0.11602964997291565,
            0.03687294200062752,
            0.9999999403953552,
        ),
    ],
    [
        0.469696968793869,
        (0.06526660174131393, 0.09636423736810684, 0.027114661410450935, 1.0),
    ],
    [
        0.4848484694957733,
        (0.08706381916999817, 0.11790782958269119, 0.046073250472545624, 1.0),
    ],
    [
        0.542424201965332,
        (
            0.09536351263523102,
            0.12620145082473755,
            0.04181394353508949,
            0.9999999403953552,
        ),
    ],
    [
        0.5636363625526428,
        (0.0690077543258667, 0.09473975002765656, 0.020241104066371918, 1.0),
    ],
    [
        0.5878787636756897,
        (0.08635130524635315, 0.1102556511759758, 0.03209475427865982, 1.0),
    ],
    [
        0.6151515245437622,
        (0.08278042078018188, 0.10866615921258926, 0.03059503808617592, 1.0),
    ],
    [
        0.6303030252456665,
        (0.09988351911306381, 0.12961478531360626, 0.03197917342185974, 1.0),
    ],
    [
        0.6575757265090942,
        (0.08673778176307678, 0.11318439990282059, 0.02206132747232914, 1.0),
    ],
    [
        0.6939393877983093,
        (0.0820535272359848, 0.11294956505298615, 0.025454571470618248, 1.0),
    ],
    [
        0.7090908885002136,
        (
            0.10943226516246796,
            0.16052745282649994,
            0.049264442175626755,
            0.9999999403953552,
        ),
    ],
    [
        0.7212120890617371,
        (0.07932015508413315, 0.11094442754983902, 0.02675677090883255, 1.0),
    ],
    [
        0.7999999523162842,
        (0.06607985496520996, 0.09544237703084946, 0.01906781829893589, 1.0),
    ],
    [
        0.8727272748947144,
        (0.06541866809129715, 0.09150668978691101, 0.02363416738808155, 1.0),
    ],
    [
        0.9121211767196655,
        (0.08682817965745926, 0.11426736414432526, 0.03219122812151909, 1.0),
    ],
    [
        0.9303029775619507,
        (
            0.12840968370437622,
            0.16026008129119873,
            0.041482843458652496,
            0.9999999403953552,
        ),
    ],
    [
        0.9424242377281189,
        (0.10437119752168655, 0.13402700424194336, 0.020978417247533798, 1.0),
    ],
    [
        0.9666666388511658,
        (
            0.15073294937610626,
            0.17535895109176636,
            0.03390835225582123,
            0.9999999403953552,
        ),
    ],
    [
        0.9999999403953552,
        (0.16969136893749237, 0.1803307831287384, 0.032433055341243744, 1.0),
    ],
]

light_brown = [
    [0.0, (0.5708065629005432, 0.3501649796962738, 0.1970381885766983, 1.0)],
    [
        0.0317460298538208,
        (0.49367770552635193, 0.27540671825408936, 0.14620208740234375, 1.0),
    ],
    [
        0.0476190447807312,
        (0.5153784155845642, 0.29007938504219055, 0.1617794781923294, 1.0),
    ],
    [
        0.07407407462596893,
        (
            0.3814314305782318,
            0.20766381919384003,
            0.09934963285923004,
            0.9999999403953552,
        ),
    ],
    [
        0.10052909702062607,
        (
            0.5555273294448853,
            0.3999195694923401,
            0.21089749038219452,
            0.9999999403953552,
        ),
    ],
    [
        0.1269841194152832,
        (0.5142614841461182, 0.3647889792919159, 0.20586630702018738, 1.0),
    ],
    [
        0.18518517911434174,
        (0.5048016905784607, 0.3217650055885315, 0.15087038278579712, 1.0),
    ],
    [
        0.22751322388648987,
        (
            0.5290141105651855,
            0.3023093640804291,
            0.13273820281028748,
            0.9999999403953552,
        ),
    ],
    [
        0.2539682388305664,
        (
            0.5779104828834534,
            0.35815101861953735,
            0.18462790548801422,
            0.9999999403953552,
        ),
    ],
    [
        0.29629629850387573,
        (0.579153299331665, 0.36728817224502563, 0.1914948970079422, 1.0),
    ],
    [
        0.31216931343078613,
        (0.502051830291748, 0.2907825708389282, 0.1361647993326187, 1.0),
    ],
    [
        0.3333333134651184,
        (
            0.5838703513145447,
            0.3919956386089325,
            0.17936120927333832,
            0.9999999403953552,
        ),
    ],
    [
        0.35449734330177307,
        (0.5153840780258179, 0.2942061126232147, 0.1372983157634735, 1.0),
    ],
    [
        0.4285714030265808,
        (0.4940497875213623, 0.27730345726013184, 0.1326170414686203, 1.0),
    ],
    [
        0.43915343284606934,
        (0.3080892562866211, 0.16651302576065063, 0.09363576769828796, 1.0),
    ],
    [
        0.4603174328804016,
        (0.5022767782211304, 0.29338252544403076, 0.14015409350395203, 1.0),
    ],
    [
        0.5132275223731995,
        (0.5019206404685974, 0.28084874153137207, 0.12904682755470276, 1.0),
    ],
    [
        0.5343915224075317,
        (0.38943779468536377, 0.20316621661186218, 0.0984918624162674, 1.0),
    ],
    [
        0.6031745672225952,
        (0.4744051992893219, 0.26563793420791626, 0.13286028802394867, 1.0),
    ],
    [
        0.6190475821495056,
        (0.4124835729598999, 0.21703405678272247, 0.12048952281475067, 1.0),
    ],
    [
        0.6455026268959045,
        (
            0.5376088619232178,
            0.35771676898002625,
            0.22880375385284424,
            0.9999999403953552,
        ),
    ],
    [
        0.6772486567497253,
        (
            0.5600335001945496,
            0.373645156621933,
            0.22475197911262512,
            0.9999999403953552,
        ),
    ],
    [
        0.7037037014961243,
        (
            0.45947176218032837,
            0.2685413956642151,
            0.14283661544322968,
            0.9999999403953552,
        ),
    ],
    [
        0.7248677015304565,
        (0.48205798864364624, 0.2517305314540863, 0.10750141739845276, 1.0),
    ],
    [
        0.820105791091919,
        (
            0.47209736704826355,
            0.24670001864433289,
            0.1043165847659111,
            0.9999999403953552,
        ),
    ],
    [
        0.8465608358383179,
        (
            0.6280598044395447,
            0.40191563963890076,
            0.21883898973464966,
            0.9999999403953552,
        ),
    ],
    [
        0.8677248358726501,
        (0.45349299907684326, 0.3230687379837036, 0.14317621290683746, 1.0),
    ],
    [
        0.9047618508338928,
        (0.3285621404647827, 0.299384742975235, 0.14560067653656006, 1.0),
    ],
    [
        0.9312168955802917,
        (0.13294872641563416, 0.18164664506912231, 0.09317649155855179, 1.0),
    ],
    [
        0.9999999403953552,
        (0.11479152739048004, 0.16931354999542236, 0.08570000529289246, 1.0),
    ],
]

dark_brown = [
    [0.0, (0.4231075942516327, 0.17851322889328003, 0.04637044668197632, 1.0)],
    [
        0.020408162847161293,
        (0.3929608464241028, 0.17128455638885498, 0.041462112218141556, 1.0),
    ],
    [
        0.09693877398967743,
        (0.3933279812335968, 0.1713070571422577, 0.041755061596632004, 1.0),
    ],
    [
        0.13265305757522583,
        (
            0.3627054989337921,
            0.14180216193199158,
            0.032953523099422455,
            0.9999999403953552,
        ),
    ],
    [
        0.20918366312980652,
        (0.3468526303768158, 0.12630079686641693, 0.028448648750782013, 1.0),
    ],
    [
        0.33673468232154846,
        (0.33606061339378357, 0.12101004272699356, 0.028406180441379547, 1.0),
    ],
    [
        0.4030612111091614,
        (
            0.33560267090797424,
            0.12246328592300415,
            0.02935335412621498,
            0.9999999403953552,
        ),
    ],
    [
        0.4285714328289032,
        (0.2935342788696289, 0.10154799371957779, 0.023280424997210503, 1.0),
    ],
    [
        0.5153061151504517,
        (0.28062331676483154, 0.09419652819633484, 0.02162769064307213, 1.0),
    ],
    [
        0.5612244606018066,
        (0.2606342136859894, 0.08153779059648514, 0.017233949154615402, 1.0),
    ],
    [
        0.6071428656578064,
        (0.2506868541240692, 0.07309570908546448, 0.013761477544903755, 1.0),
    ],
    [
        0.668367326259613,
        (0.24029503762722015, 0.06882958114147186, 0.012501269578933716, 1.0),
    ],
    [
        0.7091836333274841,
        (0.23660841584205627, 0.07025811821222305, 0.01396752055734396, 1.0),
    ],
    [
        0.7448979616165161,
        (0.19211672246456146, 0.049332115799188614, 0.00880483165383339, 1.0),
    ],
    [
        0.8061224222183228,
        (0.1851516216993332, 0.04678148776292801, 0.00802469439804554, 1.0),
    ],
    [
        0.8724489808082581,
        (
            0.18665947020053864,
            0.04876931756734848,
            0.007321999408304691,
            0.9999999403953552,
        ),
    ],
    [
        0.9081632494926453,
        (0.21302464604377747, 0.06443409621715546, 0.010481167584657669, 1.0),
    ],
    [
        1.0,
        (
            0.22274701297283173,
            0.0698438361287117,
            0.012087887153029442,
            0.9999999403953552,
        ),
    ],
]


def create_single_color_texture(material_name, color):
    # Delete material if it already exists
    if material_name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[material_name])

    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    material.use_fake_user = True
    nodes = material.node_tree.nodes

    # Get the Principled BSDF shader (default in new materials)
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
    return material


stem_colors = [
    [0.0, (0.12895609438419342, 0.13951356709003448, 0.11136160790920258, 1)],
    [0.125, (0.12929318845272064, 0.143860325217247, 0.09668125212192535, 1)],
    [0.1875, (0.09842608124017715, 0.10585431754589081, 0.06227358058094978, 1)],
    [0.25, (0.09504438936710358, 0.1134655624628067, 0.07275909930467606, 1)],
    [0.34375, (0.13039550185203552, 0.17367327213287354, 0.10978951305150986, 1)],
    [0.375, (0.13761095702648163, 0.17949910461902618, 0.10516965389251709, 1)],
    [0.4375, (0.10919235646724701, 0.12212932854890823, 0.057648103684186935, 1)],
    [0.53125, (0.10158953815698624, 0.11307650804519653, 0.049694307148456573, 1)],
    [0.59375, (0.11446765065193176, 0.1476057767868042, 0.08318386971950531, 1)],
    [0.75, (0.09773695468902588, 0.12039747834205627, 0.06930835545063019, 1)],
    [0.84375, (0.1050824522972107, 0.13193878531455994, 0.0888044610619545, 1)],
    [0.90625, (0.16442303359508514, 0.1869821399450302, 0.13162760436534882, 1)],
    [0.96875, (0.18140973150730133, 0.19513775408267975, 0.12579673528671265, 1)],
    [1.0, (0.14702947437763214, 0.15592685341835022, 0.08228161931037903, 1)],
]


def create_stem_texture(material_name: str = "StemMaterial"):
    return create_grass_texture(material_name, colors=green_color, brown_tips=False)


head_colors_old = [
    [0.0, (0.36659377813339233, 0.3909117579460144, 0.22328662872314453, 1.0)],
    [
        0.08571428805589676,
        (0.35517600178718567, 0.38066866993904114, 0.21042576432228088, 1.0),
    ],
    [
        0.17142857611179352,
        (0.35726097226142883, 0.3813251554965973, 0.22300183773040771, 1.0),
    ],
    [
        0.23571428656578064,
        (0.369564026594162, 0.3902185261249542, 0.22810818254947662, 1.0),
    ],
    [
        0.4285714328289032,
        (0.3753418028354645, 0.3963049054145813, 0.23682072758674622, 1.0),
    ],
    [
        0.4642857313156128,
        (0.35653674602508545, 0.3475547432899475, 0.1684344857931137, 1.0),
    ],
    [
        0.5428571701049805,
        (0.34926995635032654, 0.3371361792087555, 0.13804058730602264, 1.0),
    ],
    [
        0.5785714387893677,
        (0.3173617720603943, 0.3105267584323883, 0.09996134787797928, 1.0),
    ],
    [
        0.6285714507102966,
        (0.314706027507782, 0.3116900324821472, 0.11460690200328827, 1.0),
    ],
    [
        0.6714285612106323,
        (0.3015574812889099, 0.3074182868003845, 0.1437482088804245, 1.0),
    ],
    [
        0.7214285731315613,
        (0.34719082713127136, 0.3510132133960724, 0.21219110488891602, 1.0),
    ],
    [
        0.7714285850524902,
        (0.3527427613735199, 0.3598572313785553, 0.23033790290355682, 1.0),
    ],
    [
        0.8214285969734192,
        (0.2994891107082367, 0.3228338956832886, 0.18569475412368774, 1.0),
    ],
    [
        0.8571428656578064,
        (0.26403331756591797, 0.2840515077114105, 0.15029291808605194, 1.0),
    ],
    [
        0.9214285612106323,
        (0.2302587479352951, 0.24252979457378387, 0.1144275814294815, 1.0),
    ],
    [1.0, (0.22318615019321442, 0.23373138904571533, 0.10353030264377594, 1.0)],
]

head_colors = [
    [0.0, (0.09874721616506577, 0.1282682567834854, 0.005339437164366245, 1.0)],
    [
        0.04545454680919647,
        (0.19339707493782043, 0.209637850522995, 0.031827691942453384, 1.0),
    ],
    [
        0.09090909361839294,
        (0.17715367674827576, 0.23172059655189514, 0.041291698813438416, 1.0),
    ],
    [
        0.13636364042758942,
        (0.1198430210351944, 0.16371135413646698, 0.016970319673419, 1.0),
    ],
    [
        0.20454546809196472,
        (0.21190479397773743, 0.24006851017475128, 0.04718007892370224, 1.0),
    ],
    [
        0.34090909361839294,
        (
            0.2363433539867401,
            0.2517786920070648,
            0.05213143303990364,
            0.9999999403953552,
        ),
    ],
    [
        0.4318181872367859,
        (0.19114698469638824, 0.23042435944080353, 0.036918941885232925, 1.0),
    ],
    [
        0.4545454680919647,
        (0.2393912672996521, 0.27944085001945496, 0.04386387765407562, 1.0),
    ],
    [
        0.5227273106575012,
        (0.22320500016212463, 0.2691047191619873, 0.05743442475795746, 1.0),
    ],
    [
        0.5681818127632141,
        (0.2603417932987213, 0.3103073537349701, 0.07514448463916779, 1.0),
    ],
    [
        0.6136363744735718,
        (0.25245213508605957, 0.29209795594215393, 0.07518485188484192, 1.0),
    ],
    [
        0.7045454978942871,
        (0.26484203338623047, 0.29863619804382324, 0.0723295733332634, 1.0),
    ],
    [
        0.7727273106575012,
        (0.2595650553703308, 0.27731913328170776, 0.06012895330786705, 1.0),
    ],
    [
        0.8181818723678589,
        (0.28168144822120667, 0.2946336567401886, 0.056018829345703125, 1.0),
    ],
    [
        0.8636363744735718,
        (0.24378348886966705, 0.2602720856666565, 0.048858072608709335, 1.0),
    ],
    [
        0.9318181872367859,
        (
            0.22950540482997894,
            0.2506074011325836,
            0.04237670078873634,
            0.9999999403953552,
        ),
    ],
    [1.0, (0.26605167984962463, 0.2942560017108917, 0.07475169748067856, 1.0)],
]


def create_head_texture(material_name: str = "HeadMaterial"):
    return create_grass_texture(
        material_name, colors=head_colors, brown_tips=False, small=True
    )


def create_indexed_grass_texture(
    material_name: str = "IndexedMaterial",
    index=-1,
    small=False,
    material_type: MaterialType = MaterialType.LEAF,
):
    if index == -1:
        colors = head_colors
    else:
        match material_type:
            case MaterialType.LEAF:
                colors = LEAF_COLORS[index % len(LEAF_COLORS)]
            case MaterialType.HEAD:
                colors = HEAD_COLORS[index % len(HEAD_COLORS)]
            case _:
                # Should raise a warning
                colors = LEAF_COLORS[index % len(LEAF_COLORS)]

    return create_grass_texture(
        material_name, colors=colors, brown_tips=False, small=small
    )


def set_color_ramp_colors(color_ramp, colors):
    for i, color in enumerate(colors):
        if i >= len(color_ramp.elements):
            color_ramp.elements.new(color[0])
        color_ramp.elements[i].position = color[0]
        color_ramp.elements[i].color = color[1]


def create_grass_texture(
    material_name: str = "LeafMaterial",
    colors=green_color,
    vertical=True,
    brown_tips=False,
    small=False,
):
    # Delete material if it already exists
    if material_name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[material_name])

    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    material.use_fake_user = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    nodes.clear()

    tex_coord_node = nodes.new(type="ShaderNodeTexCoord")
    tex_coord_node.location = (0, 100)

    noise_node = nodes.new(type="ShaderNodeTexNoise")
    noise_node.location = (200, 300)

    links.new(tex_coord_node.outputs["UV"], noise_node.inputs["Vector"])

    mix_noise_uv_node = nodes.new(type="ShaderNodeMixRGB")
    mix_noise_uv_node.location = (400, 100)
    mix_noise_uv_node.inputs["Fac"].default_value = 0.998

    links.new(noise_node.outputs["Color"], mix_noise_uv_node.inputs["Color1"])
    links.new(tex_coord_node.outputs["UV"], mix_noise_uv_node.inputs["Color2"])

    separate_node = nodes.new(type="ShaderNodeSeparateXYZ")
    separate_node.location = (600, 300)

    links.new(mix_noise_uv_node.outputs["Color"], separate_node.inputs["Vector"])

    wave_node = nodes.new(type="ShaderNodeTexWave")
    wave_node.location = (800, 400)
    if small:
        wave_node.inputs["Scale"].default_value = 15
    else:
        wave_node.inputs["Scale"].default_value = 20
    wave_node.inputs["Distortion"].default_value = 8
    wave_node.inputs["Detail Scale"].default_value = 6

    if vertical:
        links.new(separate_node.outputs["X"], wave_node.inputs["Vector"])
    else:
        links.new(separate_node.outputs["Y"], wave_node.inputs["Vector"])

    noise_node2 = nodes.new(type="ShaderNodeTexNoise")
    noise_node2.location = (800, 0)
    if small:
        noise_node2.inputs["Scale"].default_value = 5
    else:
        noise_node2.inputs["Scale"].default_value = 8
    noise_node2.inputs["Roughness"].default_value = 0.9
    noise_node2.normalize = False
    noise_node2.inputs["Lacunarity"].default_value = 3
    # noise_node2.inputs['Distortion'].default_value = 20

    links.new(mix_noise_uv_node.outputs["Color"], noise_node2.inputs["Vector"])

    mix_noise_wave_node = nodes.new(type="ShaderNodeMix")
    mix_noise_wave_node.location = (1000, 100)

    links.new(wave_node.outputs["Fac"], mix_noise_wave_node.inputs["A"])
    links.new(noise_node2.outputs["Fac"], mix_noise_wave_node.inputs["B"])

    color_ramp_node = nodes.new(type="ShaderNodeValToRGB")
    color_ramp_node.location = (1200, 100)

    # Optionally, you can set up the color ramp stops here
    # while len(color_ramp_node.color_ramp.elements) > 0:
    #    color_ramp_node.color_ramp.elements.remove(color_ramp_node.color_ramp.elements[0])
    # num_colors = len(colors)
    set_color_ramp_colors(color_ramp_node.color_ramp, colors)

    # for i, color in enumerate(colors):
    #    if i >= len(color_ramp_node.color_ramp.elements):
    #        color_ramp_node.color_ramp.elements.new(color[0])
    #    color_ramp_node.color_ramp.elements[i].position = (color[0])
    #    color_ramp_node.color_ramp.elements[i].color = color[1]

    links.new(mix_noise_wave_node.outputs["Result"], color_ramp_node.inputs["Fac"])

    principled_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    principled_node.location = (1600, 300)
    principled_node.inputs["Roughness"].default_value = 0.1

    bump_node = nodes.new(type="ShaderNodeBump")
    bump_node.location = (1200, 300)
    links.new(mix_noise_wave_node.outputs["Result"], bump_node.inputs["Height"])

    # links.new(color_ramp_node.outputs['Color'], principled_node.inputs['Base Color'])
    links.new(bump_node.outputs["Normal"], principled_node.inputs["Normal"])

    translucent_node = nodes.new(type="ShaderNodeBsdfTranslucent")
    translucent_node.location = (1600, -100)

    # links.new(color_ramp_node.outputs['Color'], translucent_node.inputs['Color'])

    add_shader_node = nodes.new(type="ShaderNodeAddShader")
    add_shader_node.location = (2000, 100)

    links.new(principled_node.outputs["BSDF"], add_shader_node.inputs[0])
    links.new(translucent_node.outputs["BSDF"], add_shader_node.inputs[1])

    material_output_node = nodes.new(type="ShaderNodeOutputMaterial")
    material_output_node.location = (2200, 100)

    # shader_displacement_node = nodes.new(type='ShaderNodeDisplacement')
    # links.new(color_ramp_node.outputs['Alpha'], shader_displacement_node.inputs['Height'])
    # links.new(shader_displacement_node.outputs['Displacement'], material_output_node.inputs['Displacement'])

    links.new(add_shader_node.outputs["Shader"], material_output_node.inputs["Surface"])

    # Ligth lines
    light_wave_texture_node = nodes.new(type="ShaderNodeTexWave")
    light_wave_texture_node.location = (800, -350)
    light_wave_texture_node.inputs["Scale"].default_value = 3
    light_wave_texture_node.inputs["Distortion"].default_value = 0.4
    if vertical:
        links.new(separate_node.outputs["X"], light_wave_texture_node.inputs["Vector"])
    else:
        links.new(separate_node.outputs["Y"], light_wave_texture_node.inputs["Vector"])

    light_wave_color_ramp_node = nodes.new(type="ShaderNodeValToRGB")
    light_wave_color_ramp_node.location = (1000, -350)
    light_wave_color_ramp_node.color_ramp.elements[0].position = 0.95
    links.new(
        light_wave_texture_node.outputs["Fac"], light_wave_color_ramp_node.inputs["Fac"]
    )

    mix_light_color_node = nodes.new(type="ShaderNodeMixRGB")
    mix_light_color_node.location = (1300, -350)
    mix_light_color_node.blend_type = "BURN"
    mix_light_color_node.inputs["Fac"].default_value = 0.2

    links.new(color_ramp_node.outputs["Color"], mix_light_color_node.inputs["Color1"])
    links.new(
        light_wave_color_ramp_node.outputs["Color"],
        mix_light_color_node.inputs["Color2"],
    )

    # links.new(mix_light_color_node.outputs['Color'], principled_node.inputs['Base Color'])

    if brown_tips:
        # Create leaf tip texture
        mapping_node = nodes.new(type="ShaderNodeMapping")
        mapping_node.location = (400, 1000)
        mapping_node.inputs["Scale"].default_value = (5, 1, 1)

        noise_node_tip = nodes.new(type="ShaderNodeTexNoise")
        noise_node_tip.location = (600, 1000)
        noise_node_tip.inputs["Scale"].default_value = 10
        noise_node_tip.inputs["Roughness"].default_value = 0.7

        links.new(tex_coord_node.outputs["UV"], mapping_node.inputs["Vector"])
        links.new(mapping_node.outputs["Vector"], noise_node_tip.inputs["Vector"])

        color_mix_tip = nodes.new(type="ShaderNodeMixRGB")
        color_mix_tip.location = (800, 1000)
        color_mix_tip.inputs["Fac"].default_value = 0.7

        links.new(noise_node_tip.outputs["Color"], color_mix_tip.inputs["Color1"])
        links.new(tex_coord_node.outputs["UV"], color_mix_tip.inputs["Color2"])

        separate_tip_node = nodes.new(type="ShaderNodeSeparateXYZ")
        separate_tip_node.location = (1000, 1000)

        links.new(color_mix_tip.outputs["Color"], separate_tip_node.inputs["Vector"])

        map_range_node1 = nodes.new(type="ShaderNodeMapRange")
        map_range_node1.location = (1200, 1000)
        map_range_node1.inputs["From Min"].default_value = 0.75
        map_range_node1.inputs["From Max"].default_value = 0.76
        map_range_node1.inputs["To Min"].default_value = 0.0
        map_range_node1.inputs["To Max"].default_value = 1.0

        map_range_node2 = nodes.new(type="ShaderNodeMapRange")
        map_range_node2.location = (1400, 1000)
        map_range_node2.inputs["From Min"].default_value = 0.8
        map_range_node2.inputs["From Max"].default_value = 0.81
        map_range_node2.inputs["To Min"].default_value = 0.0
        map_range_node2.inputs["To Max"].default_value = 1.0

        links.new(separate_tip_node.outputs["Y"], map_range_node1.inputs["Value"])
        links.new(separate_tip_node.outputs["Y"], map_range_node2.inputs["Value"])

        color_ramp_tip_node_1 = nodes.new(type="ShaderNodeValToRGB")
        color_ramp_tip_node_1.location = (1600, 1000)
        links.new(
            mix_noise_wave_node.outputs["Result"], color_ramp_tip_node_1.inputs["Fac"]
        )
        set_color_ramp_colors(color_ramp_tip_node_1.color_ramp, light_brown)

        color_ramp_tip_node_2 = nodes.new(type="ShaderNodeValToRGB")
        color_ramp_tip_node_2.location = (1600, 800)
        links.new(
            mix_noise_wave_node.outputs["Result"], color_ramp_tip_node_2.inputs["Fac"]
        )
        set_color_ramp_colors(color_ramp_tip_node_2.color_ramp, dark_brown)

        color_mix_base = nodes.new(type="ShaderNodeMixRGB")
        color_mix_base.location = (1800, 1000)

        color_mix_tip = nodes.new(type="ShaderNodeMixRGB")
        color_mix_tip.location = (1800, 1000)

        links.new(map_range_node1.outputs["Result"], color_mix_base.inputs["Fac"])
        links.new(color_ramp_node.outputs["Color"], color_mix_base.inputs["Color1"])
        links.new(
            color_ramp_tip_node_1.outputs["Color"], color_mix_base.inputs["Color2"]
        )

        links.new(map_range_node2.outputs["Result"], color_mix_tip.inputs["Fac"])
        links.new(color_mix_base.outputs["Color"], color_mix_tip.inputs["Color1"])
        links.new(
            color_ramp_tip_node_2.outputs["Color"], color_mix_tip.inputs["Color2"]
        )

    # Stains
    stains_noise_texture_node = nodes.new(type="ShaderNodeTexNoise")
    stains_noise_texture_node.location = (800, -600)
    stains_noise_texture_node.inputs["Scale"].default_value = 24
    stains_noise_texture_node.inputs["Roughness"].default_value = 0.1

    stain_color_ramp_node = nodes.new(type="ShaderNodeValToRGB")
    stain_color_ramp_node.location = (1000, -600)
    stain_color_ramp_node.color_ramp.elements[0].position = 0.65
    stain_color_ramp_node.color_ramp.elements[1].color = (1.0, 0.954, 0.238, 1.0)

    links.new(
        stains_noise_texture_node.outputs["Fac"], stain_color_ramp_node.inputs["Fac"]
    )

    add_stain_color_node = nodes.new(type="ShaderNodeMixRGB")
    add_stain_color_node.location = (1300, -600)
    add_stain_color_node.blend_type = "ADD"

    if brown_tips:
        links.new(color_mix_tip.outputs["Color"], add_stain_color_node.inputs["Color1"])
    else:
        links.new(
            color_ramp_node.outputs["Color"], add_stain_color_node.inputs["Color1"]
        )
    links.new(
        stain_color_ramp_node.outputs["Color"], add_stain_color_node.inputs["Color2"]
    )

    links.new(
        add_stain_color_node.outputs["Color"], principled_node.inputs["Base Color"]
    )
    links.new(add_stain_color_node.outputs["Color"], translucent_node.inputs["Color"])

    return material
