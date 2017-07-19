
[//]: # extract client info from an account
[:find ?client-first-name ?client-last-name ?client-email ?client-phone ?client

 :where
 [?client :client/first-name ?client-first-name]
 [?client :client/last-name ?client-last-name]
 [?client :client/contact-email ?client-email]
 [?client :client/phone-number ?client-phone]

 [?client :client/account ?account]
 [?account :account/name "BV Beauty & Laser Clinic"]]

[//]: # extract service info from an account
 [:find ?service-name ?service-duration ?service-duration ?service
  :where

  [?service :service/name ?service-name]
  [?service :service/duration ?service-duration]
  [?service :service/price ?service-price]

  [?service :service/account ?account]
  [?account :account/name "BV Beauty & Laser Clinic"]]

[//]: # extract employee info from an account
  [:find ?employee-name ?employee
   :where

   [?employee :employee/name ?employee-name]
   [?employee :employee/account ?account]
   [?account :account/name "BV Beauty & Laser Clinic"]]
