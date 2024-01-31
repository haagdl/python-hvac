"""
02.C. CONSTRUCTION ASSEMBLIES: FLOORS
Creates construction assemblies and stores them on the construction assemblies
shelf.
"""
import pandas as pd
from hvac import Quantity
from hvac.cooling_load_calc.core import (
    Geometry,
    HeatFlowDirection,
    SurfaceFilm,
    SolidLayer,
    ConstructionAssembly
)

from hvac.cooling_load_calc.wtcb.setup import (
    MaterialShelf,
    ConstructionAssemblyShelf,
    db_path
)

Q_ = Quantity


# ------------------------------------------------------------------------------
# FLOOR CONSTRUCTION ASSEMBLY WTCB F1
# ------------------------------------------------------------------------------

def create_floor_wtcb_F1(
    t_ins: Quantity,
    T_ext: Quantity = Q_(0.0, 'degC'),
    T_int: Quantity = Q_(20.0, 'degC'),
    v_wind: Quantity = Q_(4, 'm / s')
) -> ConstructionAssembly:
    heat_flow_dir = (
        HeatFlowDirection.DOWNWARDS
        if T_ext < T_int
        else HeatFlowDirection.UPWARDS
    )
    ext_surf_film = SurfaceFilm.create(
        ID='ext_surf_film',
        geometry=Geometry(),
        heat_flow_dir=heat_flow_dir,
        T_mn=T_ext,
        is_internal_surf=False,
        wind_speed=v_wind
    )
    floor_slabs = SolidLayer.create(
        ID='floor_slabs',
        geometry=Geometry(t=Q_(12, 'cm')),
        material=MaterialShelf.load('precast-slab-heavy-concrete-t=12cm')
    )
    insulation = SolidLayer.create(
        ID='insulation',
        geometry=Geometry(t=t_ins),
        material=MaterialShelf.load('polystyrene-extruded-sheet')
    )
    screed_concrete = SolidLayer.create(
        ID='screed_concrete',
        geometry=Geometry(t=Q_(8, 'cm')),
        material=MaterialShelf.load('concrete-light-1600kg/m3')
    )
    int_surf_film = SurfaceFilm.create(
        ID='int_surf_film',
        geometry=Geometry(),
        heat_flow_dir=heat_flow_dir,
        T_mn=T_int
    )
    floor = ConstructionAssembly.create(
        ID=f'floor_wtcb_F1_t_ins={t_ins.to("cm"):~P.0f}',
        layers=[
            ext_surf_film,
            floor_slabs,
            insulation,
            screed_concrete,
            int_surf_film
        ]
    )
    floor = floor.apply_insulation_correction(
        insulation_layer_ID=insulation.ID,
        insulation_level=2,
        mechanical_fastening=None
    )
    floor.layers['floor_slabs'].num_slices = 10
    floor.layers['insulation'].num_slices = 5
    floor.layers['screed_concrete'].num_slices = 10
    return floor


# ------------------------------------------------------------------------------
# FLOOR CONSTRUCTION ASSEMBLY WTCB F2
# ------------------------------------------------------------------------------

def create_floor_wtcb_F2(
    t_ins: Quantity,
    T_ext: Quantity = Q_(0.0, 'degC'),
    T_int: Quantity = Q_(20.0, 'degC')
) -> ConstructionAssembly:
    heat_flow_dir = (
        HeatFlowDirection.DOWNWARDS
        if T_ext < T_int
        else HeatFlowDirection.UPWARDS
    )
    adj_surf_film = SurfaceFilm.create(
        ID='adj_surf_film',
        geometry=Geometry(),
        heat_flow_dir=heat_flow_dir,
        T_mn=T_ext
    )
    concrete_slab = SolidLayer.create(
        ID='concrete_slab',
        geometry=Geometry(t=Q_(12, 'cm')),
        material=MaterialShelf.load('concrete-reinforced-2%-steel')
    )
    insulation = SolidLayer.create(
        ID='insulation',
        geometry=Geometry(t=t_ins),
        material=MaterialShelf.load('polystyrene-extruded-sheet')
    )
    screed_concrete = SolidLayer.create(
        ID='screed_concrete',
        geometry=Geometry(t=Q_(8, 'cm')),
        material=MaterialShelf.load('concrete-light-1600kg/m3')
    )
    int_surf_film = SurfaceFilm.create(
        ID='int_surf_film',
        geometry=Geometry(),
        heat_flow_dir=heat_flow_dir,
        T_mn=T_int
    )
    floor = ConstructionAssembly.create(
        ID=f'floor_wtcb_F2_t_ins={t_ins.to("cm"):~P.0f}',
        layers=[
            adj_surf_film,
            concrete_slab,
            insulation,
            screed_concrete,
            int_surf_film
        ]
    )
    floor = floor.apply_insulation_correction(
        insulation_layer_ID=insulation.ID,
        insulation_level=2,
        mechanical_fastening=None
    )
    floor.layers['concrete_slab'].num_slices = 10
    floor.layers['insulation'].num_slices = 5
    floor.layers['screed_concrete'].num_slices = 10
    return floor


# ------------------------------------------------------------------------------
# FLOOR CONSTRUCTION ASSEMBLY WTCB F3
# ------------------------------------------------------------------------------

def create_floor_wtcb_F3(
    t_ins: Quantity,
    T_ext: Quantity = Q_(0.0, 'degC'),
    T_int: Quantity = Q_(20.0, 'degC'),
) -> ConstructionAssembly:
    heat_flow_dir = (
        HeatFlowDirection.DOWNWARDS
        if T_ext < T_int
        else HeatFlowDirection.UPWARDS
    )
    adj_surf_film = SurfaceFilm.create(
        ID='adj_surf_film',
        geometry=Geometry(),
        heat_flow_dir=heat_flow_dir,
        T_mn=T_ext,
    )
    floor_slab = SolidLayer.create(
        ID='floor_slab',
        geometry=Geometry(t=Q_(12, 'cm')),
        material=MaterialShelf.load('precast-slab-heavy-concrete-t=12cm')
    )
    insulation = SolidLayer.create(
        ID='insulation',
        geometry=Geometry(t=t_ins),
        material=MaterialShelf.load('polystyrene-extruded-sheet')
    )
    screed_concrete = SolidLayer.create(
        ID='screed_concrete',
        geometry=Geometry(t=Q_(8, 'cm')),
        material=MaterialShelf.load('concrete-light-1600kg/m3')
    )
    int_surf_film = SurfaceFilm.create(
        ID='int_surf_film',
        geometry=Geometry(),
        heat_flow_dir=heat_flow_dir,
        T_mn=T_int
    )
    floor = ConstructionAssembly.create(
        ID=f'floor_wtcb_F3_t_ins={t_ins.to("cm"):~P.0f}',
        layers=[
            adj_surf_film,
            floor_slab,
            insulation,
            screed_concrete,
            int_surf_film
        ]
    )
    floor = floor.apply_insulation_correction(
        insulation_layer_ID=insulation.ID,
        insulation_level=2,
        mechanical_fastening=None
    )
    floor.layers['floor_slab'].num_slices = 10
    floor.layers['insulation'].num_slices = 5
    floor.layers['screed_concrete'].num_slices = 10
    return floor


# ------------------------------------------------------------------------------
# FLOOR CONSTRUCTION ASSEMBLY WTCB F4
# ------------------------------------------------------------------------------

def create_floor_wtcb_F4(
    t_ins: Quantity,
    T_grd: Quantity,
    T_int: Quantity = Q_(20.0, 'degC')
) -> ConstructionAssembly:
    heat_flow_dir = (
        HeatFlowDirection.DOWNWARDS
        if T_grd < T_int
        else HeatFlowDirection.UPWARDS
    )
    floor_slab = SolidLayer.create(
        ID='floor_slab',
        geometry=Geometry(t=Q_(12, 'cm')),
        material=MaterialShelf.load('concrete-reinforced-2%-steel')
    )
    insulation = SolidLayer.create(
        ID='insulation',
        geometry=Geometry(t=t_ins),
        material=MaterialShelf.load('polystyrene-extruded-sheet')
    )
    screed_concrete = SolidLayer.create(
        ID='screed_concrete',
        geometry=Geometry(t=Q_(8, 'cm')),
        material=MaterialShelf.load('concrete-light-1600kg/m3')
    )
    int_surf_film = SurfaceFilm.create(
        ID='int_surf_film',
        geometry=Geometry(),
        heat_flow_dir=heat_flow_dir,
        T_mn=T_int
    )
    floor = ConstructionAssembly.create(
        ID=f'floor_wtcb_F4_t_ins={t_ins.to("cm"):~P.0f}',
        layers=[
            floor_slab,
            insulation,
            screed_concrete,
            int_surf_film
        ]
    )
    floor = floor.apply_insulation_correction(
        insulation_layer_ID=insulation.ID,
        insulation_level=2,
        mechanical_fastening=None
    )
    return floor


# ------------------------------------------------------------------------------

def main():
    t_ins = Q_(12, 'cm')

    ca_floor_wtcb_F1 = create_floor_wtcb_F1(t_ins)
    ca_floor_wtcb_F2 = create_floor_wtcb_F2(t_ins)
    ca_floor_wtcb_F3 = create_floor_wtcb_F3(t_ins)
    ca_floor_wtcb_F4 = create_floor_wtcb_F4(t_ins, T_grd=Q_(0, 'degC'))

    ConstructionAssemblyShelf.add(
        ca_floor_wtcb_F1,
        ca_floor_wtcb_F2,
        ca_floor_wtcb_F3,
        ca_floor_wtcb_F4
    )

    with pd.option_context(
            'display.max_rows', None,
            'display.max_columns', None,
            'display.width', None,
            'display.colheader_justify', 'center'
    ):
        print(ConstructionAssemblyShelf.overview(detailed=True))

    ConstructionAssemblyShelf.export_to_excel(str(db_path / 'construction_assemblies.ods'))


if __name__ == '__main__':
    main()
