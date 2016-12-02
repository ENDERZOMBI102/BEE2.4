"""Adds breakable glass."""
from conditions import make_result_setup, make_result, RES_EXHAUSTED
from instanceLocs import resolve as resolve_inst
from srctools import Property, Vec, VMF, Solid, Side, Entity, Output

import utils
import comp_consts as const

from typing import Iterator, Any, Tuple, Dict, List

LOGGER = utils.getLogger(__name__)

BREAKABLE_GLASS_CONF = {}

# For each direction, whether min/max
CORNER_NAMES = ['lowerleft', 'lowerright', 'upperleft', 'upperright']
CORNER_POINTS = {
    Vec.N: [
        (min, 0, min),
        (max, 0, min),
        (min, 0, max),
        (max, 0, max),
    ],
    Vec.S: [
        (max, 0, min),
        (min, 0, min),
        (max, 0, max),
        (min, 0, max),
    ],
    Vec.E: [
        (0, max, min),
        (0, min, min),
        (0, max, max),
        (0, min, max),
    ],
    Vec.W: [
        (0, min, min),
        (0, max, min),
        (0, min, max),
        (0, max, max),
    ],
    Vec.T: [
        (min, min, 0),
        (min, max, 0),
        (max, min, 0),
        (max, max, 0),
    ],
    Vec.B: [
        (min, max, 0),
        (min, min, 0),
        (max, max, 0),
        (max, min, 0),
    ]
}  # type: Dict[Tuple[float, float, float], List[Tuple[Any, Any, Any]]]


def glass_item_setup(conf: dict, item_id, config_dict):
    [base_inst] = resolve_inst('<{}:0>'.format(item_id))

    conf.update({
        'frame_' + name: resolve_inst('<{}:bee2_frame_{}>'.format(item_id, name))[0]
        for name in ['edge', 'single', 'ubend', 'corner']
    })
    config_dict[base_inst.casefold()] = conf


def find_glass_items(config, vmf: VMF) -> Iterator[Tuple[str, Vec, Vec, Vec, dict]]:
    # targetname -> min, max, normal, config
    glass_items = {}
    for inst in vmf.by_class['func_instance']:  # type: Entity
        try:
            conf = BREAKABLE_GLASS_CONF[inst['file'].casefold()]
        except KeyError:
            continue
        targ = inst['targetname']
        norm = Vec(x=1).rotate_by_str(inst['angles'])
        origin = Vec.from_str(inst['origin']) - 64 * norm
        try:
            bbox_min, bbox_max, group_norm, group_conf = glass_items[targ]
        except KeyError:
            # First of this group..
            bbox_min, bbox_max = origin.copy(), origin.copy()
            group_norm = norm.copy()
            glass_items[targ] = bbox_min, bbox_max, group_norm, conf
        else:
            bbox_min.min(origin)
            bbox_max.max(origin)
            assert group_norm == norm, '"{}" is inconsistently rotated!'.format(targ)
            assert group_conf is conf, '"{}" has multiple configs!'.format(targ)
        inst.remove()

    for targ, (bbox_min, bbox_max, norm, conf) in glass_items.items():
        yield targ, bbox_min, bbox_max, norm, conf


def make_frames(vmf: VMF, targ: str, conf: dict, bbox_min: Vec, bbox_max: Vec, norm: Vec):
    """Generate frames for a rectangular glass item."""
    def make_frame(frame_type, loc, angles):
        """Make a frame instance."""
        vmf.create_ent(
            classname='func_instance',
            targetname=targ,
            file=conf['frame_' + frame_type],
            # Position at the center of the block, instead of at the glass.
            origin=loc - norm * 64,
            angles=angles,
        )

    if bbox_min == bbox_max:
        # 1x1 glass..
        make_frame('single', bbox_min, norm.to_angle())
        return

    norm_axis = norm.axis()
    u_axis, v_axis = Vec.INV_AXIS[norm_axis]

    u_norm = Vec()
    v_norm = Vec()
    u_norm[u_axis] = 1
    v_norm[v_axis] = 1

    single_u = bbox_min[u_axis] == bbox_max[u_axis]
    single_v = bbox_min[v_axis] == bbox_max[v_axis]

    # If single in either direction, it needs a u-bend.
    if single_u:
        ubend_axis = v_axis
    elif single_v:
        ubend_axis = u_axis
    else:
        ubend_axis = None
    if ubend_axis is not None:
        for bend_mag, bbox in [(1, bbox_min), (-1, bbox_max)]:
            make_frame(
                'ubend',
                bbox,
                norm.to_angle_roll(Vec.with_axes(ubend_axis, bend_mag)),
            )
    else:
        # Make 4 corners.
        make_frame(
            'corner',
            bbox_min,
            norm.to_angle_roll(Vec.with_axes(v_axis, 1)),
        )
        make_frame(
            'corner',
            bbox_max,
            norm.to_angle_roll(Vec.with_axes(v_axis, -1)),
        )
        make_frame(
            'corner',
            Vec.with_axes(u_axis, bbox_min, v_axis, bbox_max, norm_axis, bbox_min),
            norm.to_angle_roll(Vec.with_axes(u_axis, 1)),
        )
        make_frame(
            'corner',
            Vec.with_axes(u_axis, bbox_max, v_axis, bbox_min, norm_axis, bbox_min),
            norm.to_angle_roll(Vec.with_axes(u_axis, -1)),
        )

    # Make straight sections.
    straight_u_pos = norm.to_angle_roll(v_norm)
    straight_u_neg = norm.to_angle_roll(-v_norm)
    straight_v_pos = norm.to_angle_roll(u_norm)
    straight_v_neg = norm.to_angle_roll(-u_norm)
    for u_pos in range(int(bbox_min[u_axis] + 128), int(bbox_max[u_axis]), 128):
        make_frame(
            'edge',
            Vec.with_axes(u_axis, u_pos, v_axis, bbox_min, norm_axis, bbox_min),
            straight_u_pos,
        )
        make_frame(
            'edge',
            Vec.with_axes(u_axis, u_pos, v_axis, bbox_max, norm_axis, bbox_min),
            straight_u_neg,
        )
    for v_pos in range(int(bbox_min[v_axis] + 128), int(bbox_max[v_axis]), 128):
        make_frame(
            'edge',
            Vec.with_axes(v_axis, v_pos, u_axis, bbox_min, norm_axis, bbox_min),
            straight_v_pos,
        )
        make_frame(
            'edge',
            Vec.with_axes(v_axis, v_pos, u_axis, bbox_max, norm_axis, bbox_min),
            straight_v_neg,
        )



@make_result_setup('BreakableGlass')
def res_breakable_glass_setup(res: Property):
    item_id = res['item']
    conf = {
        'material': res['material'],
        'offset': res.float('offset', 0.5),
        # Distance inward from the frames the glass should span.
        'border_size': res.float('border_size', 0),
        'thickness': res.float('thickness', 4),
        }

    glass_item_setup(conf, item_id, BREAKABLE_GLASS_CONF)

    return res.value


@make_result('BreakableGlass')
def res_breakable_glass(inst: Entity, res: Property):
    """Adds breakable glass to the map.

    Paramters:
        * thickness: Thickness of the collision brushes.
        * offset: Distance into the block to place the surface.
        * border_size: Distance on borders to inset by (so the shatter effects
          appear.)
        * material: Name of the func_breakable_surf material.
    """
    vmf = inst.map

    glass_items = find_glass_items(BREAKABLE_GLASS_CONF, vmf)

    for targ, bbox_min, bbox_max, norm, conf in glass_items:
        LOGGER.info('Making glass "{}"', targ)
        norm_axis = norm.axis()
        uaxis, vaxis = Vec.INV_AXIS[norm_axis]
        solid_min = bbox_min.copy()
        solid_max = bbox_max.copy()
        uv_off = 64 - conf['border_size']
        solid_min[uaxis] -= uv_off
        solid_min[vaxis] -= uv_off
        solid_max[uaxis] += uv_off
        solid_max[vaxis] += uv_off

        # This doesn't choose min/max correctly, but that's fine.
        solid_min += conf['offset'] * norm
        solid_max += (conf['offset'] + 1) * norm

        surf_solid = vmf.make_prism(solid_min, solid_max).solid
        for face in surf_solid:  # type: Side
            if face.normal() == norm:
                face.mat = conf['material']

        breakable_surf = vmf.create_ent(
            classname='func_breakable_surf',
            targetname=targ + '-surf',
            spawnflags=3,  # 'Physics damage decals, and take damage from held
            drawinfastreflection=1,
            # propdata=24,  # Glass.Window
            health=20,
            performancemode=2,  # Full gibs on all platforms
            surfacetype=0,  # Glass
            fragility=30,  # Lower fragility, so less shatters with collisions.

            error=0,  # Our corners are fine..
        )
        breakable_surf.solids.append(surf_solid)
        solid_min += norm
        solid_max -= norm

        # func_breakable_surf allows several P2 things to pass through.
        # Place a thin func_brush inside the surf to block collisions.
        # Since it's inside, the breakable will recieve physics impacts to
        # destroy it.
        clip_min = bbox_min.copy()
        clip_max = bbox_max.copy()
        clip_min[uaxis] -= 64
        clip_min[vaxis] -= 64
        clip_max[uaxis] += 64
        clip_max[vaxis] += 64
        clip_min += (conf['offset'] + 0.3) * norm
        clip_max += (conf['offset'] + 0.6) * norm

        clip = vmf.create_ent(classname='func_brush', origin=bbox_min, spawnflags=0, targetname=targ + '-clip')
        clip.solids.append(
            vmf.make_prism(
                clip_min,
                clip_max,
                mat=const.Tools.NODRAW,
            ).solid
        )

        breakable_surf.add_out(
            Output('OnBreak', targ + '-clip', 'Kill', only_once=True),
        )

        # We need to set "lowerleft", "upperright" etc keyvalues to the corner
        # locations.
        # These are used to place the shattered glass, when it breaks.
        for name, points in zip(CORNER_NAMES, CORNER_POINTS[norm.as_tuple()]):
            corner = Vec()
            for axis, axis_type in zip('xyz', points):
                if axis == norm_axis:  # solid_min is aligned to the front.
                    corner[axis] = solid_min[axis]
                elif axis_type is max:
                    corner[axis] = solid_max[axis]
                elif axis_type is min:
                    corner[axis] = solid_min[axis]
            breakable_surf[name] = corner

        make_frames(vmf, targ, conf, bbox_min, bbox_max, -norm)

    return RES_EXHAUSTED
