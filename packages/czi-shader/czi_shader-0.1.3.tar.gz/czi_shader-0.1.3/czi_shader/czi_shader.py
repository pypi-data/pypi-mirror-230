import colorsys
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Optional, Union
from xml.etree import ElementTree

import aicspylibczi
import cv2
import numpy as np
import pint
from numpy.typing import NDArray
from pint.facets.plain import PlainQuantity

T_CZI = Union[aicspylibczi.CziFile, Path, str]

def etree_to_dict(t) -> dict[str, Any]:
    '''from https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree'''

    d: dict = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text: d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def czi_hex_rgb_to_hls(color_str: str) -> tuple[float, float, float]:
    '''example: '#FFFF0014' -> (355.29411764705884, 50.0, 100.0)
    '''
    if color_str.startswith('#'):
        color_str = color_str[1:]
    if len(color_str) == 8:
        color_str = color_str[2:]
    if len(color_str) != 6:
        raise ValueError(f'invalid color_str {color_str}')

    rgb = re.findall('..', color_str)
    r, g, b = map(lambda x: int(x, 16), rgb)

    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return (h*360, l*100, s*100)


def shading_image(
    image: np.ndarray, hls: tuple[float, float, float], 
    black_v:Optional[float]=None, white_v:Optional[float]=None,
    multiply: float=1
) ->  NDArray[np.uint8]:
    '''return rgb image'''
    if black_v is None or white_v is None:
        black_v, white_v = np.percentile(image[image!=0], (1, 99.9))
    assert black_v is not None and white_v is not None
    np.clip(image, black_v, white_v, out=image)

    h, l, s = hls
    light = (image - black_v) / (white_v - black_v) * l * multiply
    np.clip(light, 0, l, out=light)
    hls_image = np.zeros((*image.shape, 3), dtype=np.uint8)
    hls_image[..., 0] = h / 2                # 从 0~360 转到 180
    hls_image[..., 1] = light * (255 / 100)  # 从 0~100 转到 255
    hls_image[..., 2] = s * (255 / 100)      # 从 0~100 转到 255
    cv2.cvtColor(hls_image, cv2.COLOR_HLS2RGB, dst=hls_image)
    return hls_image

@dataclass
class CZIPhysicalResolution:
    '''
    example input: 
    <Items>
        <Distance Id="X">
            <Value>6.5E-07</Value>
            <DefaultUnitFormat>&#181;m</DefaultUnitFormat>
        </Distance>
        <Distance Id="Y">
            <Value>6.5E-07</Value>
            <DefaultUnitFormat>&#181;m</DefaultUnitFormat>
        </Distance>
    </Items>

    '''
    x: PlainQuantity
    y: PlainQuantity

    @staticmethod
    def from_czi(czi: T_CZI) -> 'CZIPhysicalResolution':
        if not isinstance(czi, aicspylibczi.CziFile):
            czi = aicspylibczi.CziFile(czi)
        distance = czi.meta.find('.//Metadata/Scaling/Items')
        assert distance is not None, 'cannot find distance in czi meta'
        return CZIPhysicalResolution.from_xml(distance)

    @staticmethod
    def from_xml(e: ElementTree.Element):
        x = e.find('./Distance[@Id="X"]/Value')
        x_unit = e.find('./Distance[@Id="X"]/DefaultUnitFormat')
        y = e.find('./Distance[@Id="Y"]/Value')
        y_unit = e.find('./Distance[@Id="Y"]/DefaultUnitFormat')

        assert isinstance(x,  ElementTree.Element) and isinstance(x_unit,  ElementTree.Element)
        assert isinstance(y,  ElementTree.Element) and isinstance(y_unit,  ElementTree.Element)
        x, x_unit = x.text, x_unit.text
        y, y_unit = y.text, y_unit.text
        assert isinstance(x, str) and isinstance(y, str)
        assert isinstance(x_unit, str) and isinstance(y_unit, str)

        return CZIPhysicalResolution(
            x=pint.Quantity(float(x), x_unit) / pint.Quantity(1, 'pixel'),
            y=pint.Quantity(float(y), y_unit) / pint.Quantity(1, 'pixel'),
        )

@dataclass
class CZIChannel:
    '''
    example input: 
    <Channel Id="Channel:2" Name="EGFP">
     <Low>0.0043691845281902137</Low>
     <High>0.14451909533769555</High>
     <BitCountRange>16</BitCountRange>
     <PixelType>Gray16</PixelType>
     <DyeName>EGFP</DyeName>
     <ShortName>EGFP</ShortName>
     <IlluminationType>Fluorescence</IlluminationType>
     <DyeMaxEmission>509</DyeMaxEmission>
     <DyeMaxExcitation>488</DyeMaxExcitation>
     <DyeId>McNamara-Boswell-0828</DyeId>
     <DyeDatabaseId>66071726-cbd4-4c41-b371-0a6eee4ae9c5</DyeDatabaseId>
     <Color>#FF00FF5B</Color>
     <ColorMode>Palette</ColorMode>
     <OriginalColor>#FF00FF5B</OriginalColor>
     <PaletteName>HeatMap</PaletteName>
     <IsSelected>false</IsSelected>
    </Channel>
    '''

    id                : int
    name              : str
    bit_count_range   : int
    pixel_type        : str
    dye_name          : str
    short_name        : str
    illumination_type : str
    dye_max_emission  : int
    dye_max_excitation: int
    dye_id            : str
    dye_database_id   : str
    color             : str
    original_color    : str
    
    color_mode  : Optional[Literal['Custom', 'Palette']] = None
    palette_name: Optional[str] = None

    gamma: Optional[float] = None
    low  : Optional[float] = None
    high : Optional[float] = None

    is_selected: Optional[bool] = None

    @staticmethod
    def from_czi(czi: T_CZI) -> list['CZIChannel']:
        if not isinstance(czi, aicspylibczi.CziFile):
            czi = aicspylibczi.CziFile(czi)
        metas = czi.meta.findall('.//DisplaySetting/Channels/')
        return [CZIChannel.from_xml(meta) for meta in metas]

    @staticmethod
    def from_xml(e: ElementTree.Element):
        dic: dict = etree_to_dict(e)['Channel']
        assert isinstance(dic, dict)
        return CZIChannel(
            id                 = int(e.attrib['Id'].split(':')[-1]),
            name               = e.attrib['Name'],
            bit_count_range    = int(dic.get('BitCountRange', '0')),
            pixel_type         = dic.get('PixelType', ''),
            dye_name           = dic.get('DyeName', ''),
            short_name         = dic.get('ShortName', ''),
            illumination_type  = dic.get('IlluminationType', ''),
            dye_max_emission   = int(dic.get('DyeMaxEmission', '0')),
            dye_max_excitation = int(dic.get('DyeMaxExcitation', '0')),
            dye_id             = dic.get('DyeId', ''),
            dye_database_id    = dic.get('DyeDatabaseId', ''),
            color              = dic.get('Color', ''),
            original_color     = dic.get('OriginalColor', ''),
            
            color_mode   = dic.get('ColorMode'),
            palette_name = dic.get('PaletteName'),
            
            gamma = float(dic['Gamma']) if 'Gamma' in dic else None,
            low   = float(dic['Low']) if 'Low' in dic else None,
            high  = float(dic['High']) if 'High' in dic else None,
            
            is_selected=dic['IsSelected'] == 'true' if 'IsSelected' in dic else None,
        )

    @property
    def hls(self):
        return czi_hex_rgb_to_hls(self.color)

    @property
    def int_low(self):
        if self.low is not None:
            return int(self.low * (2 ** self.bit_count_range - 1))

    @property
    def int_high(self):
        if self.high is not None:
            return int(self.high * (2 ** self.bit_count_range - 1))

    def shading(
        self, image: np.ndarray, 
        black_v:Optional[float]=None, white_v:Optional[float]=None,
        multiply: float=1
    ) -> NDArray[np.uint8]:
        '''return rgb image'''
        if (
            (black_v is white_v is None) and 
            (self.int_low is not None and self.int_high is not None)
        ):
            black_v, white_v = self.int_low, self.int_high
        return shading_image(image, self.hls, black_v, white_v, multiply=multiply)

def merge_channels(rgb_imgs: list[NDArray[np.uint8]]) -> NDArray[np.uint8]:
    merged_image = np.sum(rgb_imgs, axis=0, dtype='uint16')
    np.clip(merged_image, 0, 255, out=merged_image)
    return merged_image.astype('uint8')

def shading_czi(
    czi: T_CZI, scale_factor: float=1,
    black_v:Optional[float]=None, white_v:Optional[float]=None,
    multiply: float=1
) -> NDArray[np.uint8]:
    '''return rgb image'''
    if not isinstance(czi, aicspylibczi.CziFile):
        czi = aicspylibczi.CziFile(czi)
    images = []
    chs = CZIChannel.from_czi(czi)

    for ch in chs:
        image = czi.read_mosaic(scale_factor=scale_factor, C=ch.id)[0]
        image = ch.shading(image, black_v=black_v, white_v=white_v, multiply=multiply)
        images.append(image)
    return merge_channels(images)


@dataclass
class CZIImageInfo:
    ''' example input:
    <Image>
        <AcquisitionDateAndTime>2019-04-27T05:46:48.1796863Z</AcquisitionDateAndTime>
        <SizeC>4</SizeC>
        <ComponentBitCount>16</ComponentBitCount>
        <PixelType>Gray16</PixelType>
        <SizeX>73692</SizeX>
        <SizeY>53448</SizeY>
        <SizeS>1</SizeS>
        <SizeM>899</SizeM>
        <OriginalCompressionMethod>JpgXr</OriginalCompressionMethod>
        <OriginalEncodingQuality>85</OriginalEncodingQuality>
        <AcquisitionDuration>3484246.2876000004</AcquisitionDuration>
    </Image>
    '''
    acquisition_date_and_time: datetime
    
    size_c             : int
    component_bit_count: int

    pixel_type: str
    size_x    : int
    size_y    : int
    size_s    : int
    size_m    : int
    
    original_compression_method: str
    original_encoding_quality  : int
    acquisition_duration       : float

    @property
    def width(self): return self.size_x
    @property
    def height(self): return self.size_y

    @staticmethod
    def from_czi(czi: T_CZI) -> 'CZIImageInfo':
        if not isinstance(czi, aicspylibczi.CziFile):
            czi = aicspylibczi.CziFile(czi)
        image_info = czi.meta.find('.//Metadata/Information/Image')
        assert image_info is not None, 'cannot find image info in czi meta'
        return CZIImageInfo.from_xml(image_info)
    
    @staticmethod
    def from_xml(e: ElementTree.Element):
        dic: dict = etree_to_dict(e)['Image']
        assert isinstance(dic, dict)
        return CZIImageInfo(
            acquisition_date_and_time   = datetime.fromisoformat(dic['AcquisitionDateAndTime']),
            size_c                      = int(dic['SizeC']),
            component_bit_count         = int(dic['ComponentBitCount']),
            pixel_type                  = dic['PixelType'],
            size_x                      = int(dic['SizeX']),
            size_y                      = int(dic['SizeY']),
            size_s                      = int(dic['SizeS']),
            size_m                      = int(dic['SizeM']),
            original_compression_method = dic['OriginalCompressionMethod'],
            original_encoding_quality   = int(dic['OriginalEncodingQuality']),
            acquisition_duration        = float(dic['AcquisitionDuration']),
        )

@dataclass
class CZIMeta:
    image_info: CZIImageInfo
    resolution: CZIPhysicalResolution
    channels  : list[CZIChannel]

    @staticmethod
    def from_czi(czi: T_CZI) -> 'CZIMeta':
        if not isinstance(czi, aicspylibczi.CziFile):
            czi = aicspylibczi.CziFile(czi)
        return CZIMeta.from_xml(czi.meta)

    @staticmethod
    def from_xml(e: ElementTree.Element):
        resolution_xml = e.find('.//Metadata/Scaling/Items')
        assert resolution_xml is not None, 'cannot find resolution in czi meta'

        image_info_xml = e.find('.//Metadata/Information/Image')
        assert image_info_xml is not None, 'cannot find image info in czi meta'

        return CZIMeta(
            image_info=CZIImageInfo.from_xml(image_info_xml),
            resolution=CZIPhysicalResolution.from_xml(resolution_xml),
            channels=[CZIChannel.from_xml(ch) for ch in e.findall('.//DisplaySetting/Channels/')],
        )
