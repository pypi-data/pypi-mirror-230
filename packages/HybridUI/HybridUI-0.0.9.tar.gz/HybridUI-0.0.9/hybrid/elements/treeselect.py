from typing import List
from ..element import Element

# Annahme: `Element` und andere Abhängigkeiten sind bereits definiert

from typing import List, Any
from ..element import Element

class TreeSelect(Element):

    def __init__(
            self, 
            content: List[Element] = None,
            allowClear = None,
            autoClearSearchValue = None,
            bordered = None,
            defaultValue = None,
            disabled = None,
            popupClassName = None,
            popupMatchSelectWidth = None,
            dropdownRender = None,
            dropdownStyle = None,
            fieldNames = None,
            filterTreeNode = None,
            getPopupContainer = None,
            labelInValue = None,
            listHeight = None,
            loadData = None,
            maxTagCount = None,
            maxTagPlaceholder = None,
            maxTagTextLength = None,
            multiple = None,
            notFoundContent = None,
            placeholder = None,
            placement = None,
            searchValue = None,
            showCheckedStrategy = None,
            showSearch = None,
            size = None,
            status = None,
            suffixIcon = None,
            switcherIcon = None,
            tagRender = None,
            treeCheckable = None,
            treeCheckStrictly = None,
            treeData = None,
            treeDataSimpleMode = None,
            treeDefaultExpandAll = None,
            treeDefaultExpandedKeys = None,
            treeExpandAction = None,
            treeExpandedKeys = None,
            treeIcon = None,
            treeLoadedKeys = None,
            treeLine = None,
            treeNodeFilterProp = None,
            treeNodeLabelProp = None,
            value = None,
            virtual = None,
            onChange = None,
            onDropdownVisibleChange = None,
            onSearch = None,
            onSelect = None,
            onTreeExpand = None,
            ):
        super().__init__(component='TreeSelect')
        self.children = content
        self._props["allowClear"] = allowClear
        self._props["autoClearSearchValue"] = autoClearSearchValue
        self._props["bordered"] = bordered
        self._props["defaultValue"] = defaultValue
        self._props["disabled"] = disabled
        self._props["popupClassName"] = popupClassName
        self._props["popupMatchSelectWidth"] = popupMatchSelectWidth
        self._props["dropdownRender"] = dropdownRender
        self._props["dropdownStyle"] = dropdownStyle
        self._props["fieldNames"] = fieldNames
        self._props["filterTreeNode"] = filterTreeNode
        self._props["getPopupContainer"] = getPopupContainer
        self._props["labelInValue"] = labelInValue
        self._props["listHeight"] = listHeight
        self._props["loadData"] = loadData
        self._props["maxTagCount"] = maxTagCount
        self._props["maxTagPlaceholder"] = maxTagPlaceholder
        self._props["maxTagTextLength"] = maxTagTextLength
        self._props["multiple"] = multiple
        self._props["notFoundContent"] = notFoundContent
        self._props["placeholder"] = placeholder
        self._props["placement"] = placement
        self._props["searchValue"] = searchValue
        self._props["showCheckedStrategy"] = showCheckedStrategy
        self._props["showSearch"] = showSearch
        self._props["size"] = size
        self._props["status"] = status
        self._props["suffixIcon"] = suffixIcon
        self._props["switcherIcon"] = switcherIcon
        self._props["tagRender"] = tagRender
        self._props["treeCheckable"] = treeCheckable
        self._props["treeCheckStrictly"] = treeCheckStrictly
        self._props["treeData"] = treeData
        self._props["treeDataSimpleMode"] = treeDataSimpleMode
        self._props["treeDefaultExpandAll"] = treeDefaultExpandAll
        self._props["treeDefaultExpandedKeys"] = treeDefaultExpandedKeys
        self._props["treeExpandAction"] = treeExpandAction
        self._props["treeExpandedKeys"] = treeExpandedKeys
        self._props["treeIcon"] = treeIcon
        self._props["treeLoadedKeys"] = treeLoadedKeys
        self._props["treeLine"] = treeLine
        self._props["treeNodeFilterProp"] = treeNodeFilterProp
        self._props["treeNodeLabelProp"] = treeNodeLabelProp
        self._props["value"] = value
        self._props["virtual"] = virtual
        if not onChange == None:
            self._props["onChange"] = onChange
        if not onDropdownVisibleChange == None:
            self._props["onDropdownVisibleChange"] = onDropdownVisibleChange
        if not onSearch == None:
            self._props["onSearch"] = onSearch
        if not onSelect == None:
            self._props["onSelect"] = onSelect
        if not onTreeExpand == None:
            self._props["onTreeExpand"] = onTreeExpand
