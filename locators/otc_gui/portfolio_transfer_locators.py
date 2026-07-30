class PortfolioTransferLocators:

    # Entry section
    ENTRY_TYPE = "#puEntryType input"

    FILE_UPLOAD = "#puUpload input[type='file']"

    # Transfer Type
    TRANSFER_TYPE = "#puTransferType input"
    ACCOUNT_TRANSFER_OPTION = "xpath=//*[text()='Account Transfer']"

    # Book
    BOOK_FIELD = "#puBook input"

    # Source System Fields
    CLIENT_ID_MW = "#puClientIdMw input"

    CM_ID_MW = "#puCmIdMw input"

    CLIENT_ID_OTHER = "#puClientIdOther input"

    CM_ID_OTHER = "#puCmIdOther input"

    # MtM
    MTM_FIELD = "#puMtmAdj input"
    MTM_ADJ_OPTION = "xpath=//*[text()='No']"

    # Buttons
    CREATE_PORTFOLIO_TRANSFER = "#puTransfer"

    CLEAR_BUTTON = "#puClear"

    # Result Grid
    RESULT_GRID = "#puGrid"

    UPLOAD_STATUS = "td[cellindex='2'] a"

    TARGET_BOOK_RESULT = "td[cellindex='3'] div"

    DESCRIPTION_RESULT = "td[cellindex='5'] div"