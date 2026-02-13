(function(startEl, endEl, startStr, endStr) {

    function parseDate(str) {
        // Accepts "YYYY-MM-DD HH:MM"
        // Also works with ISO strings like "2026-02-15T18:00"
        return new Date(str.replace(" ", "T"));
    }

    function forceSetDate(el, dateObj) {
        var ngEl = angular.element(el);
        var ctrl = ngEl.controller('ngModel');

        if (!ctrl) {
            console.log("No ngModel controller found");
            return;
        }

        // Disable Angular mutation layers
        ctrl.$parsers.length = 0;
        ctrl.$formatters.length = 0;
        ctrl.$validators = {};
        ctrl.$asyncValidators = {};
        ctrl.$render = function () {};

        // Push value through Angular
        ctrl.$setViewValue(dateObj);
        ctrl.$commitViewValue();

        // Force DOM display
        el.value = dateObj.toLocaleString();

        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));

        var scope = ngEl.scope() || ngEl.isolateScope();
        if (scope && !scope.$$phase) {
            scope.$apply();
        }

        console.log("Value forced:", dateObj);
    }

    var startDate = parseDate(startStr);
    var endDate   = parseDate(endStr);

    forceSetDate(startEl, startDate);
    forceSetDate(endEl, endDate);

})(arguments[0], arguments[1], arguments[2], arguments[3]);
