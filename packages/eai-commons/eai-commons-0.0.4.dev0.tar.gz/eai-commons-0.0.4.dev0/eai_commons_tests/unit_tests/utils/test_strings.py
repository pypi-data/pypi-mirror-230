import asyncio

from eai_commons.utils import strings


def test_random_id():
    raw_lower_uid = strings.random_id(with_hypper=True)
    raw_upper_uid = strings.random_id(upper=True, with_hypper=True)
    lower_uid = strings.random_id()
    upper_uid = strings.random_id(upper=True)

    print(raw_lower_uid)
    print(raw_upper_uid)
    print(lower_uid)
    print(upper_uid)


def test_mask_string():
    lower_uid = strings.random_id()
    mask1 = strings.mask_string(lower_uid, 4, 4)
    mask2 = strings.mask_string_position(lower_uid, 4, len(lower_uid) - 4)
    assert mask1 == mask2


def test_compress_decompress():
    import sys

    data = """
根据来源于网络的资料，"秀才"账号被封禁的原因可能是因为他被举报存在税收违法行为。亳州市税务局已经收到了相关举报材料，并正在进行调查工作。这可能是封禁他账号的部分原因。

然而，根据低优先级的参考资料，没有明确提到"秀才"账号被封禁的具体原因。只是提到了可能的原因，包括账号涉及违规内容、被他人举报存在异常行为或内容、涉嫌侵权等。这些原因都是基于社交平台的使用规定和法律法规进行的封禁处理。

综合以上资料，可以推断"秀才"账号被封禁的原因可能是因为他被举报存在税收违法行为，并违反了社交平台的使用规定。然而，由于没有提供更具体的信息，无法确定封禁的具体原因。    
    """

    bytes_ = strings.compress(data, "GBK")
    print(f"source size: {sys.getsizeof(data)}")
    print(f"compress size: {len(bytes_)}")
    decompress_ = strings.decompress(bytes_, "GBK")
    assert data == decompress_


def test_dicts_to_csv_content():
    dicts = [{
        "name": "周杰伦",
        "song": "兰亭序"
    }]
    content = strings.dicts_to_csv_content(dicts)
    assert content
    assert isinstance(content, str)
    print(content)
