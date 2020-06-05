import Component from './utils/component';
import * as dom from './utils/dom';
import * as type from './utils/type';
import * as utils from './utils/index';

import defaultOptions from './defaultOptions';

export default class bulmaCollapsible extends Component {
	constructor(element, options = {}) {
		super(element, options, defaultOptions);

		//Bind events to current class
		this.onTriggerClick = this.onTriggerClick.bind(this);
		this.onTransitionEnd = this.onTransitionEnd.bind(this);

		// Initiate plugin
		this._init();
	}

	/**
	 * Initiate all DOM element corresponding to selector
	 * @method
	 * @return {Array} Array of all Plugin instances
	 */
	static attach(selector = '.is-collapsible', options = {}) {
		return super.attach(selector, options, defaultOptions);
	}

	/**
	 * Initiate plugin
	 * @method init
	 * @return {void}
	 */
	_init() {
		// Save original element height
		this._originalHeight = this.element.style.height;

		this._parent = this.element.dataset.parent;
		if (this._parent) {
			const parent = this.options.container.querySelector(`#${this._parent}`);
			this._siblings = dom.querySelectorAll(this.options.selector, parent) || [];
		}

		this._triggers = this.options.container.querySelectorAll(`[data-action="collapse"][href="#${this.element.id}"], [data-action="collapse"][data-target="${this.element.id}"]`) || null;
		if (this._triggers) {
			this._triggers.on('click touch', this.onTriggerClick);
		}

		this._transitionEvent = utils.whichTransitionEvent();
		if (this._transitionEvent) {
			this.element.on(this._transitionEvent, this.onTransitionEnd);
		}

		// Set initial state
		if (this.element.classList.contains('is-active')) {
			this.expand();
		}  else {
			this.collapse();
		}
	}

	destroy() {
		// Unbind all event listener from triggers
		if (this._triggers) {
			this._triggers.off('click touch', this.onTriggerClick, false);
		}
	}

	/**
	 * Check is element is collapsed
	 * @method init
	 * @return {Boolean} true if element is collapsed(closed) else false
	 */
	collapsed() {
		return this._collapsed;
	}

	/**
	 * Expand(Open) element
	 * @method init
	 * @return {void}
	 */
	expand() {
		if (typeof this._collapsed !== 'undefined' && !this._collapsed) {
			return;
		}

		this.emit('before:expand', this);

		this._collapsed = false;
		
		// Close all siblings (based on data-parent attribute) if allowMultiple option set to False
		if (this._parent && !type.BooleanParse(this.options.allowMultiple)) {
			this._siblings.forEach(sibling => {
				if (!sibling.isSameNode(this.element)) {
					if (sibling.bulmaCollapsible) {
						sibling.bulmaCollapsible('close');
					}
				}
			});
		}

		// Apply style to show (expand) collapsible element
		this.element.style.height = this.element.scrollHeight + 'px';
		this.element.classList.add('is-active');
		this.element.setAttribute('aria-expanded', true);

		// Add 'is-active" class to all triggers
		if (this._triggers) {
			this._triggers.forEach(trigger => {
				trigger.classList.add('is-active');
			});
		}

		this.emit('after:expand', this);
	}

	/**
	 * Shortcut to expand method
	 */
	open()
	{
		this.expand();
	}

	/**
	 * Collapse(Close) element
	 * @method init
	 * @return {void}
	 */
	collapse() {
		if (typeof this._collapsed !== 'undefined' && this._collapsed) {
			return;
		}

		this.emit('before:collapse', this);

		this._collapsed = true;

		// Apply style to hide (collapse) collapsible element
		this.element.style.height = 0;
		this.element.classList.remove('is-active');
		this.element.setAttribute('aria-expanded', false);

		// Remove 'is-active" class from all triggers
		if (this._triggers) {
			this._triggers.forEach(trigger => {
				trigger.classList.remove('is-active');
			});
		}

		this.emit('after:collapse', this);
	}

	/**
	 * Shortcut to collapse method
	 */
	close()
	{
		this.collapse();
	}

	/**
	 * Trigger listener to Toggle element state
	 * @method init
	 * @param {event} event
	 * @return {void}
	 */
	onTriggerClick(event) {
		event.preventDefault();

		if (this.collapsed()) {
			event.currentTarget.classList.add('is-active');
			this.expand();
		} else {
			event.currentTarget.classList.remove('is-active');
			this.collapse();
		}
	}

	/**
	 * Listener on CSS transition end
	 * @param {event} event
	 * @return {void}
	 */
	onTransitionEnd(event) {
		if (!this._collapsed) {
			this.element.style.height = this._originalHeight;
		}
	}
}
