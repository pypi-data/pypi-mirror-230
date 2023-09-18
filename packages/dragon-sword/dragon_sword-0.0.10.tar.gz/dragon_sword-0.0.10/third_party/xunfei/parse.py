from utils.data import VoiceAsrData, Sentence, Content
from third_party.wrm.log import logger


class XFData:
    # 0-最终结果；1-中间结果
    type_final = "0"
    type_tmp = "1"

    # n-普通词；s-顺滑词（语气词）；p-标点
    word_normal = "n"
    word_tone = "s"
    word_punc = "p"


class XFAsrData(VoiceAsrData):
    def __init__(self, asr_data: dict):
        super().__init__(asr_data)
        self._content = None

    def parse(self):
        self._content = self._parse()
        logger.debug("%s", self._content)

    def sentences(self) -> str:
        return str(self._content)

    def _new_sentence(self, seg_id, speaker, seg_begin, word_begin) -> Sentence:
        s = Sentence(speaker, seg_id)
        s.time_begin(self._get_start(seg_begin, word_begin))
        return s

    @staticmethod
    def _get_start(seg_begin: str, word_begin: int) -> int:
        return int(seg_begin) + word_begin * 10

    @staticmethod
    def _get_end(seg_begin: str, word_end: int) -> int:
        """
        返回毫秒
        """
        return int(seg_begin) + word_end * 10

    def _parse(self) -> Content:
        """
        解析asr结果，获取识别的句子结果
        输出数据：
        """
        content = Content()
        s = None
        for seg in self._asr_data:
            cn_sentence = seg["cn"]["st"]
            # 只要最终结果
            if cn_sentence["type"] != XFData.type_final:
                continue
            # logger.debug(seg)
            seg_id = seg["seg_id"]
            seg_begin = cn_sentence["bg"]
            seg_end = cn_sentence["ed"]
            # 拼接一句话
            for item in cn_sentence["rt"][0]["ws"]:
                word_info = item["cw"][0]
                speaker = word_info["rl"]
                # 换人了
                if s and speaker != s.speaker:
                    logger.debug("get %s", s)
                    content.add(s)
                    s = None

                word = word_info["w"]
                # 还没开始新句，是个标点，看看要不要归到上一句
                if s is None and word_info["wp"] == XFData.word_punc:
                    # 归到上一句了
                    if content.add_punc(word, speaker):
                        logger.debug("%s to last sentence", word_info)
                        continue

                word_begin = word_info["wb"]
                word_end = word_info["we"]
                if s is None:
                    s = self._new_sentence(seg_id, speaker, seg_begin, word_begin)
                s.add_text(word)
                s.time_end(self._get_end(seg_end, word_end))
        if s:
            content.add(s)
        return content
