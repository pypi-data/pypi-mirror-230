import nlpaug.augmenter.word as naw
import pysbd
import random
import numpy as np
import nltk
import torch
import logging

try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

try:
    nltk.data.find("corpora/omw-1.4")
except LookupError:
    nltk.download("omw-1.4")

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("wordnet")


class DataAugmentation:

    """
    augment text by companies names random shuffling, back-translation and words synonyms
    """

    def __init__(
        self, translation_model_config_by_name=dict(), all_ner_mentions_pool=set()
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Device: {self.device}")

        self.ner_mentions_pool = all_ner_mentions_pool  # can either input list of all ner mentions or just add iteratively

        self.translation_model_by_name = dict()
        if not translation_model_config_by_name:
            logging.warning(
                """No back-translations have been given as input. If you are planning to use
        the back-translation augmentation, you need to add this in when initialising the module. 
        Example: translation_model_config_by_name=
        {
          'de': 
            {
                'from_model': 'Helsinki-NLP/opus-mt-en-de',
                'to_model': 'Helsinki-NLP/opus-mt-de-en'
            }
        }

        Find available models here: https://huggingface.co/Helsinki-NLP"""
            )
        else:
            self._download_back_translation_models(translation_model_config_by_name)

        synonym_regex = "NE[0-9]*"  # pattern for indicating companies names
        self.synonym_augmenter = naw.SynonymAug(
            aug_src="wordnet", aug_p=0.3, stopwords_regex=synonym_regex
        )  # initiate augmenter with synonyms (using companies names pattern as stopwords)

        # (translation on the whole text is not stable, sometimes it translates only two-three sentences)
        self.seg = pysbd.Segmenter(language="en", char_span=True)

    def _create_mask_mapping(self, ner_mentions: list) -> dict:
        """to build mask mapping dictionary for a row"""
        mask_mapping = dict()
        for i, name in enumerate(ner_mentions):
            self.ner_mentions_pool.add(name)
            mask_mapping[name] = f"NE{str(i)}"
        return mask_mapping

    def _mask_company_names(self, text: str, mask_mapping: dict) -> tuple:
        """# for masking companies names"""
        for entity_name, mask in list(mask_mapping.items()):
            text = text.replace(entity_name, mask)
        return text

    def _unmask_company_names(self, text: str, mask_mapping: dict) -> str:
        """for unmasking companies names"""
        for entity_name, mask in list(mask_mapping.items()):
            text = text.replace(mask, entity_name)
        return text

    def _download_back_translation_models(
        self, translation_model_config_by_name: dict
    ) -> None:
        logging.info("Donwloading back-translation models")
        for k, v in translation_model_config_by_name.items():
            logging.info(f"""From: {v["from_model"]}, To: {v["to_model"]}""")
            try:
                back_translation_aug_model = naw.BackTranslationAug(
                    from_model_name=v["from_model"],
                    to_model_name=v["to_model"],
                    device=self.device,
                )
                self.translation_model_by_name[k] = back_translation_aug_model
            except Exception as e:
                logging.error(e)

    def augmentation_by_back_translation(
        self, text: str, mask_mapping: dict, sentence_segmentation=True
    ) -> tuple:
        """
        Output augmented text result and language used (None for both if requirements
        not met.)
        List of back-translations corresponds to languages with which translations were done
        """
        if not self.translation_model_by_name:
            logging.error(
                f"""There are no downloaded back-translation models. Please re-initialise the module"""
            )

        unmasked_texts = []
        aug_langs = []
        masked_text = self._mask_company_names(text, mask_mapping)

        for lang, back_translation_aug in self.translation_model_by_name.items():
            if sentence_segmentation:
                augmented_text = " ".join(
                    [
                        back_translation_aug.augment(sent)[0]
                        for sent in self.seg.processor(masked_text).process()
                    ]
                )
            else:
                augmented_text = back_translation_aug.augment(masked_text)[0]
                # coin flip for random company names replacement
            if random.random() > 0.5:
                new_names = np.random.choice(
                    list(self.ner_mentions_pool), size=len(mask_mapping), replace=False
                )
                mask_mapping = dict(zip(new_names, mask_mapping.values()))
            unmasked_text = self._unmask_company_names(augmented_text, mask_mapping)
            if unmasked_text != text:
                unmasked_texts.append(unmasked_text)
                aug_langs.append(lang)

        return unmasked_texts, aug_langs

    def augmentation_by_shuffling(self, text: str, mask_mapping: dict) -> tuple:
        """
        Entities in original text are randomly replaced by others from the pool.
        """
        masked_text = self._mask_company_names(text, mask_mapping)
        new_names = np.random.choice(
            list(self.ner_mentions_pool), size=len(mask_mapping), replace=False
        )
        mask_mapping = dict(zip(new_names, mask_mapping.values()))
        augmented_text = self._unmask_company_names(masked_text, mask_mapping)
        return augmented_text

    def augmentation_by_synonyms(self, text: str, mask_mapping: dict) -> tuple:
        """
        Random words are replaced by synonyms
        """
        masked_text = self._mask_company_names(text, mask_mapping)
        augmented_text_result = None
        augmented_text = self.synonym_augmenter.augment(masked_text)[0]
        augmented_text = (
            augmented_text.replace(" ’ ", "’")
            .replace("“ ", "“")
            .replace(" ”", "”")
            .replace(" ' ", "'")
        )

        # coin flip for random company names replacement
        if random.random() > 0.5:
            new_names = np.random.choice(
                list(self.ner_mentions_pool), size=len(mask_mapping), replace=False
            )
            mask_mapping = dict(zip(new_names, mask_mapping.values()))

        unmasked_text = self._unmask_company_names(augmented_text, mask_mapping)
        if unmasked_text != text:
            augmented_text_result = unmasked_text
        return augmented_text_result  # will be None if requirements are not met
