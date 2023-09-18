from typing import Union
from .multilingual.wikimedia import get_wikimedia_auto_classes
from .multilingual.oscar_dummy import get_oscar_dummy_classes
from .multilingual.colossal_oscar import get_colossal_oscar_auto_classes
from .multilingual.eurlex import get_eurlex_auto_classes
from .multilingual.legal_mc4 import get_legal_mc4_auto_classes
from .nl.sonar import get_sonar_classes

import importlib


ALL_DATASET_IMPORTS = [
    # multilingual
    # curlicat
    ".multilingual.curlicat.CurlicatBGDataset",
    ".multilingual.curlicat.CurlicatHRDataset",
    ".multilingual.curlicat.CurlicatHUDataset",
    ".multilingual.curlicat.CurlicatPLDataset",
    ".multilingual.curlicat.CurlicatRODataset",
    ".multilingual.curlicat.CurlicatSKDataset",
    ".multilingual.curlicat.CurlicatSLDataset",
    # macocu
    ".multilingual.macocu.MacocuBGDataset",
    ".multilingual.macocu.MacocuHRDataset",
    ".multilingual.macocu.MacocuELDataset",
    # ".multilingual.macocu.MacocuSQDataset",
    # ".multilingual.macocu.MacocuBSDataset",
    ".multilingual.macocu.MacocuCADataset",
    # ".multilingual.macocu.MacocuISDataset",
    # ".multilingual.macocu.MacocuMKDataset",
    ".multilingual.macocu.MacocuMTDataset",
    # ".multilingual.macocu.MacocuCNRDataset",
    ".multilingual.macocu.MacocuSRDataset",
    ".multilingual.macocu.MacocuSLDataset",
    # ".multilingual.macocu.MacocuTRDataset",
    ".multilingual.macocu.MacocuUKDataset",
    # redpajama
    ".multilingual.redpajama.RedPajamaBookDataset",
    # ".multilingual.redpajama.RedPajamaArxivDataset",
    ".multilingual.redpajama.RedPajamaStackexchangeDataset",
    # en
    ".en.wikihow.WikihowDataset",
    ".en.pes2o.PeS2oDataset",
    ".en.proof_pile.ProofPileDataset",
    ".en.dialogstudio.DialogstudioDataset",
    # bg
    ".bg.bgnc_admin_eur.BGNCAdminEURDataset",
    ".bg.bgnc_news_corpus.BGNCNewsCorpusDataset",
    ".bg.bulgarian_news.BulgarianNewsDataset",
    ".bg.bulnc.BulNCDataset",
    # de
    ".de.openlegaldata.OpenLegalDataDataset",
    ".de.dewac.DEWacDataset",
    # ga
    ".ga.ga_bilingual_legistation.GABilingualLegislationDataset",
    ".ga.ga_universal_dependencies.GAUniversalDependenciesDataset",
    # hr
    ".hr.hrwac.HRWACDataset",
    ".hr.styria_news.StyriaNewsDataset",
    ".hr.croatian_news_engri.CroatianNewsENGRIDataset",
    # it
    ".it.itwac.ITWacDataset",
    # mt
    ".mt.korpus_malti.KorpusMaltiDataset",
    # nl
    *get_sonar_classes(),
    ".nl.sonar_new_media.SonarNewMediaDataset",
    # sl
    ".sl.cc_gigafida.CCGigaFidaDataset",
    ".sl.academic_slovene_kas.AcademicSloveneKASDataset",
    ".sl.slwac_web.SLWaCWebDataset",
    # sk
    ".sk.sk_court_decisions.SKCourtDecisionsDataset",
    ".sk.sk_laws.SKLawsDataset",
    # cs
    ".cs.syn_v9.SynV9Dataset",
    # da
    ".da.danish_gigaword.DanishGigawordDataset",
    # danish_parliament_corpus.DanishParliamentCorpusDataset,
    ".da.danewsroom.DANewsroomDataset",
    ".da.dk_clarin.DKClarinDataset",
    # fr
    ".fr.cabernet.CaBeRnetDataset",
    # no
    ".no.norwegian_cc.NorwegianCCNNDataset",
    ".no.norwegian_cc.NorwegianCCNODataset",
    # nak.NAKDataset,
    # nbdigital.NBDigitalDataset,
    # maalfrid_2021.Maalfrid2021Dataset,
    # parlamint.ParlaMintDataset,
    # parliamentary_proceedings.ParliamentaryProceedingsDataset,
    # sakspapir_nno.SakspapirNNODataset,
    # pl
    # ".pl.luna_pl.LunaPL",  ### BAD data
    ".pl.pl_nkjp.NKJPPodkorpusMilionowyDataset",
    ".pl.pl_parliamentary_corpus.PLParliamentaryCorpusDataset",
    # pt
    ".pt.parlamento_pt.ParlamentoPtDataset",
    ".pt.brwac.BrWacDataset",
    # lt
    ".lt.seimas_lt_en.SeismasLTENDataset",
    # lv
    ".lv.state_related_latvian_web.StateRelatedLatvianWebDataset",
    # el
    ".el.greek_legal_code.GreekLegalCodeDataset",
    ".el.greek_web_corpus.GreekWebCorpus",
    # et
    ".et.estonian_reference_corpus.EstonianReferenceCorpusDataset",
    ".et.enc.ENC2021Dataset",
    # eu
    ".eu.euscrawl.EUSCrawlDataset",
    # es
    ".es.spanish_legal.SpanishLegalDataset",
    # ".es.escorpius.ESCorpiusDataset",  # based on CC => use OSCAR instead
    # fi
    ".fi.ylenews.YLENewsDataset",
    # sv
    ".sv.sv_gigaword.SVGigawordDataset",
    # sr
    ".sr.srpkor.SrpKorDataset",
    # ro
    ".ro.marcell_legislative_subcorpus_v2.MarcellLegislativeSubcorpusV2Dataset",
    # uk
    ".uk.uk_laws.UKLawsDataset",
    # code
    ".code.starcoder.StarcoderDataset",
]


def get_class_by_import_string(
    import_string_or_cls: Union[str, object], relative_base_package: str = "lm_datasets.datasets"
):
    """
    Import dataset class based on import string

    Allowed formats:
    - ".lang.DatasetClass"   # relative
    - "lm_datasets.lang.DatasetClass"  # absolute
    """

    if isinstance(import_string_or_cls, str):
        # import from string
        if import_string_or_cls.startswith("."):  # relative import
            package = relative_base_package
        else:
            package = None  # absolute

        import_split = import_string_or_cls.split(".")
        cls_name = import_split[-1]
        mod_str = ".".join(import_split[:-1])

        mod = importlib.import_module(mod_str, package=package)

        return getattr(mod, cls_name)
    else:
        return import_string_or_cls  # already object, no need to import from string


ALL_DATASET_CLASSES = (
    [get_class_by_import_string(clss) for clss in ALL_DATASET_IMPORTS]
    + get_oscar_dummy_classes()
    + get_eurlex_auto_classes()
    + get_legal_mc4_auto_classes()
    + get_wikimedia_auto_classes()
    + get_colossal_oscar_auto_classes()
)
