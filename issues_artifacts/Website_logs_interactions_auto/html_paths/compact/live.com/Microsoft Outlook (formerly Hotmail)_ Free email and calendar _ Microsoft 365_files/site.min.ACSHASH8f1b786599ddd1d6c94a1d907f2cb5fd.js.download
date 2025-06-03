/*******************************************************************************
 * Copyright 2018 Adobe
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ******************************************************************************/
(function() {
    "use strict";

    let count = 0;
    const prefix = "__footnote";

    /**
     * Jumps to elements location without being hidden by the page navigation menu (if any)
     * @param {Event} event 
     * @param {JQuery Object} jumpToElement 
     * @returns 
     */
    function scrollToLocation(event, jumpToElement) {

        const pagenavElement = document.querySelector(".pagenav .bg-body.stuck-depth");

        if (!pagenavElement) {
            return;
        }

        event.preventDefault();

        const offSet = jumpToElement.offset();

        if (!offSet) {
            return;
        }

        const jumpToElementOffset = offSet.top;
        const pagenavNavMenuHeight = pagenavElement.offsetHeight;

        window.scrollTo({
            top: jumpToElementOffset - pagenavNavMenuHeight * 2 - 10,
            left: 0,
            behavior: 'smooth'
        });

    }

    /**
     * For bi-directional linking, when a link with the class 'ms-rte-link'
     * (link created in RTE) is clicked on, the footnote's href and the
     * referring link's id attribute, will be set to some value starting with
     * '#__footnote' respectively.
     * @param {HTMLElement} link the `ms-rte-link` element
     * @param {Event} e the click event
     * @returns 
     */
    function setClickedElement(link, e) {

        const clickedElementsSelector = link.getAttribute("href");

        if (!clickedElementsSelector || clickedElementsSelector.charAt(0) !== '#') {
            return;
        }

        scrollToLocation(e, $(clickedElementsSelector));

        const clickedElementsHrefToId = clickedElementsSelector.substring(1);
        const linkedFootnote = document.getElementById(clickedElementsHrefToId);

        if (!linkedFootnote) {
            return;
        }

        const currentId = link.getAttribute("id");

        if (currentId) {
            linkedFootnote.setAttribute("href", "#" + currentId);
        } else {
            const linkId = prefix + count;
            link.setAttribute("id", linkId);
            linkedFootnote.setAttribute("href", "#" + linkId);
            count++;
        }
    }

    /**
     * Add event listener to the anchor element on the click event to expand the target href element
     * and then focus and scroll to the target element
     * @param {HTMLElement} link the anchor element
     * @returns
     */
    function setExpandEventListener(link) {
        link.addEventListener('click', function (e) {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                // get the target element's parent element that has class 'ocr-faq-item__content'
                const faqItem = target.closest('.ocr-faq-item__content');
                
                // get the child element that with selector '.button-group > button'
                const button = faqItem?.querySelector('.button-group > button');
                if (button) {
                    // if the button has class 'collapsed', then click the button to expand the target element
                    if (button.classList.contains('collapsed')) {
                        e.preventDefault();
                        button.click();
                    }
                    // move the focus to the target element
                    target.focus();
                    // scroll page to the button element
                    button.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    }

    /**
     * Document ready handler and DOM mutation observers. Initializes Carousel components as necessary.
     *
     * @private
     */
    function onDocumentReady() {
        $('a.ms-rte-link').on('click', function (e) {
            setClickedElement(this, e);
        });

        // Add event listener to all the anchor element on the click event to expand the target href element
        document.querySelectorAll('.footnote__item a').forEach(function (element) {
            setExpandEventListener(element);
        });
    }

    if (document.readyState !== "loading") {
        onDocumentReady();
    } else {
        document.addEventListener("DOMContentLoaded", onDocumentReady);
    }

}());
