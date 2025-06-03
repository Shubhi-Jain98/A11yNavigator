
(function (document) {
    document.addEventListener("DOMContentLoaded", () => {
      const attrElement = $(".ocr-accordion .btn-collapse");

      /**
       * Data attributes for accordion elements.
       * @typedef {Object} DataAttributes
       * @property {string} off - Data attribute value when the element is collapsed.
       * @property {string} on - Data attribute value when the element is not collapsed.
       */
      const dataAttributes = {
        "bi-bhvr": { off: "7", on: "8" },
        "bi-ct": { off: "Accordion Expand", on: "Accordion Collapse" },
      };

      /**
       * Update data attributes based on the collapse state.
       * @param {Object} currentObj - Current collapse instance.
       */
      const updateDataAttribute = (currentObj) => {
        const isCollapsed =
          currentObj?.triggerElement.classList.contains("collapsed");

        Object.entries(dataAttributes).forEach(([attribute, values]) => {
          const dataAttrValue = isCollapsed ? values.off : values.on;
          currentObj.triggerElement.setAttribute(
            `data-${attribute}`,
            dataAttrValue
          );
        });
      };

      /**
       * Get instances of the Collapse.
       * @type {Array<Object>}
       */
      const collapseInst = window.ocrReimagine.CollapseExtension.getInstances();

      const filteredAccordionItems = collapseInst.filter(item =>{
            return item.triggerElement.classList.contains('ocr-accordion-item__header'); 
      });
      
      if (attrElement.length > 0) {
        // Attach event listeners for onHidden and onShown events.
        filteredAccordionItems.forEach((instance) => {
          instance.el.addEventListener(
            "onHidden",
            updateDataAttribute.bind(this, instance)
          );
          instance.el.addEventListener(
            "onShown",
            updateDataAttribute.bind(this, instance)
          );
        });
      }
    });
  })(document);