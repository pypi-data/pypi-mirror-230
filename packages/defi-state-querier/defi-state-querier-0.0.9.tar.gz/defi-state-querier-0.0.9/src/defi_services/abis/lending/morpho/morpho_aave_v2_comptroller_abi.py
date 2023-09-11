import json

MORPHO_AAVE_V2_COMPTROLLER = json.loads('''
[
  {
    "inputs": [],
    "name": "UnauthorisedLiquidate",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UnauthorisedWithdraw",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UserNotMemberOfMarket",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "AddressIsZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "AmountIsZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "BorrowingNotEnabled",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "UnauthorisedBorrow",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ClaimRewardsPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ExceedsMaxBasisPoints",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketAlreadyCreated",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketIsNotListedOnAave",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketNotCreated",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MarketPaused",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MaxNumberOfMarkets",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "MaxSortedUsersCannotBeZero",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ZeroAddress",
    "type": "error"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_borrower",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceInP2P",
        "type": "uint256"
      }
    ],
    "name": "Borrowed",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_p2pSupplyAmount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_p2pBorrowAmount",
        "type": "uint256"
      }
    ],
    "name": "P2PAmountsUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_p2pBorrowDelta",
        "type": "uint256"
      }
    ],
    "name": "P2PBorrowDeltaUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_p2pSupplyDelta",
        "type": "uint256"
      }
    ],
    "name": "P2PSupplyDeltaUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_from",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceInP2P",
        "type": "uint256"
      }
    ],
    "name": "Supplied",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_user",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceInP2P",
        "type": "uint256"
      }
    ],
    "name": "BorrowerPositionUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_user",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceInP2P",
        "type": "uint256"
      }
    ],
    "name": "SupplierPositionUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_p2pSupplyIndex",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_p2pBorrowIndex",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_poolSupplyIndex",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_poolBorrowIndex",
        "type": "uint256"
      }
    ],
    "name": "P2PIndexesUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "name": "P2PDeltasIncreased",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "address",
        "name": "_liquidator",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_liquidated",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolTokenBorrowed",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amountRepaid",
        "type": "uint256"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolTokenCollateral",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amountSeized",
        "type": "uint256"
      }
    ],
    "name": "Liquidated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_supplier",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_receiver",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceInP2P",
        "type": "uint256"
      }
    ],
    "name": "Withdrawn",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_repayer",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_onBehalf",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceOnPool",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_balanceInP2P",
        "type": "uint256"
      }
    ],
    "name": "Repaid",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_aaveIncentivesController",
        "type": "address"
      }
    ],
    "name": "AaveIncentivesControllerSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_newStatus",
        "type": "bool"
      }
    ],
    "name": "ClaimRewardsPauseStatusSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "components": [
          {
            "internalType": "uint64",
            "name": "supply",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "borrow",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "withdraw",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "repay",
            "type": "uint64"
          }
        ],
        "indexed": false,
        "internalType": "struct Types.MaxGasForMatching",
        "name": "_defaultMaxGasForMatching",
        "type": "tuple"
      }
    ],
    "name": "DefaultMaxGasForMatchingSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_entryPositionsManager",
        "type": "address"
      }
    ],
    "name": "EntryPositionsManagerSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_exitPositionsManager",
        "type": "address"
      }
    ],
    "name": "ExitPositionsManagerSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_newIncentivesVaultAddress",
        "type": "address"
      }
    ],
    "name": "IncentivesVaultSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_interestRatesManager",
        "type": "address"
      }
    ],
    "name": "InterestRatesSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "IsBorrowPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isDeprecated",
        "type": "bool"
      }
    ],
    "name": "IsDeprecatedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "IsLiquidateBorrowPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "IsLiquidateCollateralPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "IsRepayPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "IsSupplyPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "IsWithdrawPausedSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "_reserveFactor",
        "type": "uint16"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "_p2pIndexCursor",
        "type": "uint16"
      }
    ],
    "name": "MarketCreated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_newValue",
        "type": "uint256"
      }
    ],
    "name": "MaxSortedUsersSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "_newValue",
        "type": "uint16"
      }
    ],
    "name": "P2PIndexCursorSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_isP2PDisabled",
        "type": "bool"
      }
    ],
    "name": "P2PStatusSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_newStatus",
        "type": "bool"
      }
    ],
    "name": "PartialPauseStatusSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "bool",
        "name": "_newStatus",
        "type": "bool"
      }
    ],
    "name": "PauseStatusSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint16",
        "name": "_newValue",
        "type": "uint16"
      }
    ],
    "name": "ReserveFactorSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amountClaimed",
        "type": "uint256"
      }
    ],
    "name": "ReserveFeeClaimed",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_user",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "_amountClaimed",
        "type": "uint256"
      },
      {
        "indexed": true,
        "internalType": "bool",
        "name": "_traded",
        "type": "bool"
      }
    ],
    "name": "RewardsClaimed",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_newRewardsManagerAddress",
        "type": "address"
      }
    ],
    "name": "RewardsManagerSet",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "_newTreasuryVaultAddress",
        "type": "address"
      }
    ],
    "name": "TreasuryVaultSet",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "BORROWING_MASK",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "DEFAULT_LIQUIDATION_CLOSE_FACTOR",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "HEALTH_FACTOR_LIQUIDATION_THRESHOLD",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "MAX_BASIS_POINTS",
    "outputs": [
      {
        "internalType": "uint16",
        "name": "",
        "type": "uint16"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "MAX_NB_OF_MARKETS",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "NO_REFERRAL_CODE",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "ONE",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "ST_ETH",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "ST_ETH_BASE_REBASE_INDEX",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "VARIABLE_INTEREST_MODE",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "aaveIncentivesController",
    "outputs": [
      {
        "internalType": "contract IAaveIncentivesController",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "addressesProvider",
    "outputs": [
      {
        "internalType": "contract ILendingPoolAddressesProvider",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "name": "borrow",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "_maxGasForMatching",
        "type": "uint256"
      }
    ],
    "name": "borrow",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "borrowBalanceInOf",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "inP2P",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "onPool",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "borrowMask",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address[]",
        "name": "_assets",
        "type": "address[]"
      },
      {
        "internalType": "bool",
        "name": "_tradeForMorphoToken",
        "type": "bool"
      }
    ],
    "name": "claimRewards",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "claimedAmount",
        "type": "uint256"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address[]",
        "name": "_poolTokens",
        "type": "address[]"
      },
      {
        "internalType": "uint256[]",
        "name": "_amounts",
        "type": "uint256[]"
      }
    ],
    "name": "claimToTreasury",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_underlyingToken",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "_reserveFactor",
        "type": "uint16"
      },
      {
        "internalType": "uint16",
        "name": "_p2pIndexCursor",
        "type": "uint16"
      }
    ],
    "name": "createMarket",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "defaultMaxGasForMatching",
    "outputs": [
      {
        "internalType": "uint64",
        "name": "supply",
        "type": "uint64"
      },
      {
        "internalType": "uint64",
        "name": "borrow",
        "type": "uint64"
      },
      {
        "internalType": "uint64",
        "name": "withdraw",
        "type": "uint64"
      },
      {
        "internalType": "uint64",
        "name": "repay",
        "type": "uint64"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "deltas",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "p2pSupplyDelta",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "p2pBorrowDelta",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "p2pSupplyAmount",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "p2pBorrowAmount",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "entryPositionsManager",
    "outputs": [
      {
        "internalType": "contract IEntryPositionsManager",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "exitPositionsManager",
    "outputs": [
      {
        "internalType": "contract IExitPositionsManager",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "enum Types.PositionType",
        "name": "_positionType",
        "type": "uint8"
      }
    ],
    "name": "getHead",
    "outputs": [
      {
        "internalType": "address",
        "name": "head",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getMarketsCreated",
    "outputs": [
      {
        "internalType": "address[]",
        "name": "",
        "type": "address[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "enum Types.PositionType",
        "name": "_positionType",
        "type": "uint8"
      },
      {
        "internalType": "address",
        "name": "_user",
        "type": "address"
      }
    ],
    "name": "getNext",
    "outputs": [
      {
        "internalType": "address",
        "name": "next",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "incentivesVault",
    "outputs": [
      {
        "internalType": "contract IIncentivesVault",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IEntryPositionsManager",
        "name": "_entryPositionsManager",
        "type": "address"
      },
      {
        "internalType": "contract IExitPositionsManager",
        "name": "_exitPositionsManager",
        "type": "address"
      },
      {
        "internalType": "contract IInterestRatesManager",
        "name": "_interestRatesManager",
        "type": "address"
      },
      {
        "internalType": "contract ILendingPoolAddressesProvider",
        "name": "_lendingPoolAddressesProvider",
        "type": "address"
      },
      {
        "components": [
          {
            "internalType": "uint64",
            "name": "supply",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "borrow",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "withdraw",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "repay",
            "type": "uint64"
          }
        ],
        "internalType": "struct Types.MaxGasForMatching",
        "name": "_defaultMaxGasForMatching",
        "type": "tuple"
      },
      {
        "internalType": "uint256",
        "name": "_maxSortedUsers",
        "type": "uint256"
      }
    ],
    "name": "initialize",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "interestRatesManager",
    "outputs": [
      {
        "internalType": "contract IInterestRatesManager",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "isClaimRewardsPaused",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolTokenBorrowed",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_poolTokenCollateral",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_borrower",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "name": "liquidate",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "market",
    "outputs": [
      {
        "internalType": "address",
        "name": "underlyingToken",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "reserveFactor",
        "type": "uint16"
      },
      {
        "internalType": "uint16",
        "name": "p2pIndexCursor",
        "type": "uint16"
      },
      {
        "internalType": "bool",
        "name": "isCreated",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isPartiallyPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isP2PDisabled",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "marketPauseStatus",
    "outputs": [
      {
        "internalType": "bool",
        "name": "isSupplyPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isBorrowPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isWithdrawPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isRepayPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isLiquidateCollateralPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isLiquidateBorrowPaused",
        "type": "bool"
      },
      {
        "internalType": "bool",
        "name": "isDeprecated",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "maxSortedUsers",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "p2pBorrowIndex",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "p2pSupplyIndex",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pool",
    "outputs": [
      {
        "internalType": "contract ILendingPool",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "poolIndexes",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "lastUpdateTimestamp",
        "type": "uint32"
      },
      {
        "internalType": "uint112",
        "name": "poolSupplyIndex",
        "type": "uint112"
      },
      {
        "internalType": "uint112",
        "name": "poolBorrowIndex",
        "type": "uint112"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_onBehalf",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "name": "repay",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "rewardsManager",
    "outputs": [
      {
        "internalType": "contract IRewardsManager",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_aaveIncentivesController",
        "type": "address"
      }
    ],
    "name": "setAaveIncentivesController",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_newStatus",
        "type": "bool"
      }
    ],
    "name": "setAssetAsCollateral",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "internalType": "uint64",
            "name": "supply",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "borrow",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "withdraw",
            "type": "uint64"
          },
          {
            "internalType": "uint64",
            "name": "repay",
            "type": "uint64"
          }
        ],
        "internalType": "struct Types.MaxGasForMatching",
        "name": "_defaultMaxGasForMatching",
        "type": "tuple"
      }
    ],
    "name": "setDefaultMaxGasForMatching",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IEntryPositionsManager",
        "name": "_entryPositionsManager",
        "type": "address"
      }
    ],
    "name": "setEntryPositionsManager",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IExitPositionsManager",
        "name": "_exitPositionsManager",
        "type": "address"
      }
    ],
    "name": "setExitPositionsManager",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IIncentivesVault",
        "name": "_incentivesVault",
        "type": "address"
      }
    ],
    "name": "setIncentivesVault",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IInterestRatesManager",
        "name": "_interestRatesManager",
        "type": "address"
      }
    ],
    "name": "setInterestRatesManager",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsBorrowPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsClaimRewardsPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isDeprecated",
        "type": "bool"
      }
    ],
    "name": "setIsDeprecated",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsLiquidateBorrowPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsLiquidateCollateralPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isP2PDisabled",
        "type": "bool"
      }
    ],
    "name": "setIsP2PDisabled",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsPausedForAllMarkets",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsRepayPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsSupplyPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "_isPaused",
        "type": "bool"
      }
    ],
    "name": "setIsWithdrawPaused",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "_newMaxSortedUsers",
        "type": "uint256"
      }
    ],
    "name": "setMaxSortedUsers",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "_p2pIndexCursor",
        "type": "uint16"
      }
    ],
    "name": "setP2PIndexCursor",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "_newReserveFactor",
        "type": "uint16"
      }
    ],
    "name": "setReserveFactor",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IRewardsManager",
        "name": "_rewardsManager",
        "type": "address"
      }
    ],
    "name": "setRewardsManager",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_treasuryVault",
        "type": "address"
      }
    ],
    "name": "setTreasuryVault",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_onBehalf",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "name": "supply",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_onBehalf",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "_maxGasForMatching",
        "type": "uint256"
      }
    ],
    "name": "supply",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "supplyBalanceInOf",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "inP2P",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "onPool",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "treasuryVault",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      }
    ],
    "name": "updateIndexes",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "name": "userMarkets",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_poolToken",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "name": "withdraw",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
''')